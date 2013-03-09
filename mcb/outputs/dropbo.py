import os
import gzip
import StringIO

from mcb.outputs import Output, FakeFile
from mcb.utils.dropbo import DropboxMixin

class DropboxOutput(Output, DropboxMixin):

  def setup(self):
    Output.setup(self)
    DropboxMixin.setup(self)

    self.addConfig('dropbox_base_directory', 'Dropbox Base Directory', default='MyCloudBackup')

  def prepare(self):
    self.client = self.getClient()

  def getPath(self, name, bucket):
    path = '/' + self.dropbox_base_directory + '/' + self.prefix

    if bucket:
      path += '/' + bucket

    path += '/' + name

    return path

  def set(self, name, data, bucket=None, mode='w'):
    path = self.getPath(name, bucket)

    fileObj = data if hasattr(data, 'read') else StringIO.StringIO(data)
    self.client.put_file(path, fileObj, overwrite=True)

  def get(self, name, bucket=None):
    path = self.getPath(name, bucket)

    f = self.client.get_file(path)
    return f.read()

  def getStream(self, name, bucket=None, mode='r+'):
    path = self.getPath(name, bucket)

    mode = mode.replace('b', '')

    if mode == 'r':
      return self.client.get_file(path)
    else:
      return FakeFile(name, bucket, mode, self, self.tmpPath)


