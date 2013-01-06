import json
import os, time
from mcb.services import Service

import dropbox

class DropboxService(Service):

  def setup(self):
    self.name = 'dropbox'

    self.addConfig('app_key', default='1ykd6aqi5m05m0t')
    self.addConfig('app_secret', default='qs5ga0gd61fxuz3')

    self.addConfig('username')
    self.addConfig('access_token', default='')
    self.addConfig('access_token_secret', default='')

    self.session = None
    self.client = None
    self.meta = {}

  def getOutputPrefix(self):
    return 'dropbox.' + self.username

  def loadMetaData(self):
    mfile = self.output.get('.metadata')[0]
    if mfile:
      data = mfile.read()
      meta = json.loads(data)

      if type(meta) == dict:
        self.meta = meta

  def saveMetaData(self):
      self.output.set('.metadata', data=json.dumps(self.meta))

  def getClient(self):
    self.session = sess = dropbox.session.DropboxSession(
      self.app_key,
      self.app_secret,
      'dropbox'
    )

    if not self.access_token:
      request_token = sess.obtain_request_token()
      url = sess.build_authorize_url(request_token)
      print "url:", url
      print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
      raw_input()

      access_token = sess.obtain_access_token(request_token)
      self.access_token = access_token.key
      self.access_token_secret = access_token.secret
    else:
      sess.set_token(self.access_token, self.access_token_secret)

    client = dropbox.client.DropboxClient(sess)
    return client

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

