import os
import gzip
import StringIO

from mcb.outputs import Output
from mcb.utils.dropbo import DropboxMixin

def dropboxopen(path, mode, client, tmpPath):
  mode = mode.replace('b', '')

  if mode == 'r':
    return client.get_file(path)
  else:
    return DropboxFile(path, mode, client, tmpPath)

class DropboxFile(file):

  def __init__(self, path, mode, client, tmpPath):
    localPath = tmpPath + '/' + path[1:].replace('/', '_')

    # touch the file so we can open it for reading and writing
    super(DropboxFile, self).__init__(localPath, 'w+b')

    if mode not in ['w', 'w+']:
      # we have to download the dropbox file first
      remoteFile = client.get_file(path)
      chunk = 10000
      while True:
        data = remoteFile.read(chunk)
        if not data:
          break
        self.write(data)

      # now we have to seek to the right position, depending on mode
      if mode == 'r+':
        self.seek(0)
      elif mode in ['a', 'a+']:
        self.seek(0, 2)
      else:
        raise Exception('Unknown mode: {m}'.format(m=mode))

      self.client = client
      self.dropboxPath = path

  def close(self):
    self.seek(0, 0)
    self.client.put_file(self.dropboxPath, self, overwrite=True)
    super(DropboxFile, self).close()

class DropboxOutput(Output, DropboxMixin):

  def setup(self):
    Output.setup(self)
    DropboxMixin.setup(self)

    self.addConfig('dropbox_base_directory', default='MyCloudBackup')

  def prepare(self):
    self.client = self.getClient()
    self.tmpPath = self.getTmpPath()

  def set(self, name, data, bucket=None, mode='w'):
    path = '/' + self.dropbox_base_directory + '/' + self.prefix

    if bucket:
      path += '/' + bucket

    path += '/' + name

    fileObj = StringIO.StringIO(data)
    self.client.put_file(path, fileObj)

  def get(self, name, bucket=None):
    path = '/' + self.dropbox_base_directory + '/' + self.prefix

    if bucket:
      path += '/' + bucket

    path += '/' + name

    f = self.client.get_file(path)
    return f.read()

  def getStream(self, name, bucket=None, mode='r+'):
    path = '/' + self.dropbox_base_directory + '/' + self.prefix

    if bucket:
      path += '/' + bucket

    path += '/' + name

    return dropboxopen(path, mode, client=self.client, tmpPath=self.tmpPath)
