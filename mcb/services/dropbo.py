import json
import os, time

from mcb.services import Service
from mcb.utils.dropbo import DropboxMixin

import dropbox

class DropboxService(DropboxMixin, Service):

  def setup(self):
    Service.setup(self)
    DropboxMixin.setup(self)

    self.meta = {}

  def getPluginOutputPrefix(self):
    return self.username

  def loadMetaData(self):
    mfile = self.output.get('.metadata')[0]
    if mfile:
      data = mfile.read()
      meta = json.loads(data)

      if type(meta) == dict:
        self.meta = meta

  def saveMetaData(self):
      self.output.set('.metadata', data=json.dumps(self.meta))

  def downloadDir(self, dir):
    meta = self.client.metadata(dir)

    for item in meta['contents']:
      if item['is_dir']:
        self.downloadDir(item['path'])
      else:
        self.downloadFile(item)

  def downloadFile(self, fileItem):
    path = origPath = fileItem['path']

    if origPath in self.meta and fileItem['rev'] == self.meta[origPath]:
      # the file revision has not changed, we already have the latest version
      # nothing to do...
      return

    self.logger.debug('Downloading file: ' + path)

    dfile = self.client.get_file(path)

    path = path[1:]
    outfile = self.output.getStream(
      os.path.basename(path),
      os.path.dirname(path),
      mode = 'w'
    )

    chunk = 10000
    while True:
      data = dfile.read(chunk)
      if not data:
        break
      outfile.write(data)

    outfile.close()
    self.meta[origPath] = fileItem['rev']

    # save metadata after each processed folder
    self.saveMetaData()

  def runBackup(self):
    self.loadMetaData()

    self.client = self.getClient()
    self.downloadDir('/')
