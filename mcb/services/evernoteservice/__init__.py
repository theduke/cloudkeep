import os, time, sys
import json, csv
from datetime import datetime
import urllib, urlparse
from pprint import pprint
import mimetypes

from mcb.services import Service
from mcb.services.evernoteservice.auth import GeekNoteAuth

import evernote.edam.userstore.UserStore as UserStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.notestore.NoteStore as NoteStore
from evernote.edam.notestore.ttypes import NoteFilter
import thrift.protocol.TBinaryProtocol as TBinaryProtocol
import thrift.transport.THttpClient as THttpClient
import oauth2 as oauth

class EvernoteService(Service):

  apiConsumerKey = 'theduke-1826'
  apiConsumerSecret = 'a5a3083746d0af5a'

  EN_HOST = 'www.evernote.com'

  EN_REQUEST_TOKEN_URL = "https://" + EN_HOST + "/oauth"
  EN_ACCESS_TOKEN_URL = "https://" + EN_HOST + "/oauth"
  EN_AUTHORIZE_URL = "https://" + EN_HOST + "/OAuth.action"

  EN_USERSTORE_URIBASE = "https://" + EN_HOST + "/edam/user"

  def setup(self):
    self.name = 'evernote'

    self.addConfig('token', internal=True, default='')

    self.addConfig('username')
    self.addConfig('password')

    self.addConfig('add_note_files', 'bool', default=False,
      description="Create a file for each note with the note body")

    self.addConfig('create_json', 'bool', default=True,
      description="Create a json file with note data")

    self.addConfig('create_csv', 'bool', default=True,
      description="Create a csv file with note data")

    #self.token = 'S=s1:U=7d551:E=1438936cbd4:C=13c31859fd5:P=1cd:A=en-devtoken:H=fe3a88a49092f79a6213cb01a4ae0521'

    self.tagMap = {}

  def getPluginOutputPrefix(self):
    return self.username

  def initClient(self):
    self.checkVersion()
    if not self.token:
      self.logger.info("Trying to acquire auth token")

      auth = GeekNoteAuth()

      auth.url['base'] = self.EN_HOST

      auth.consumerKey = self.apiConsumerKey
      auth.consumerSecret = self.apiConsumerSecret
      auth.username = self.username
      auth.password = self.password

      self.token = auth.getToken()

      self.logger.info("Got auth token: {tok}".format(tok=self.token))

    self.noteStore = self.getNoteStore(self.token)

  def getUserStore(self):
      userStoreHttpClient = THttpClient.THttpClient(self.EN_USERSTORE_URIBASE)
      userStoreProtocol = TBinaryProtocol.TBinaryProtocol(userStoreHttpClient)
      userStore = UserStore.Client(userStoreProtocol)

      return userStore

  def getNoteStore(self, authToken):
      userStore = self.getUserStore()
      noteStoreUrl = userStore.getNoteStoreUrl(authToken)
      noteStoreHttpClient = THttpClient.THttpClient(noteStoreUrl)
      noteStoreProtocol = TBinaryProtocol.TBinaryProtocol(noteStoreHttpClient)
      noteStore = NoteStore.Client(noteStoreProtocol)

      return noteStore

  def checkVersion(self):
    versionOK = self.getUserStore().checkVersion("Python EDAMTest",
                                   UserStoreConstants.EDAM_VERSION_MAJOR,
                                   UserStoreConstants.EDAM_VERSION_MINOR)
    if not versionOK:
        raise Exception('Old API version')

  def getNote(self, notebook, guid):
    data = self.noteStore.getNote(
      self.token,
      guid,
      True,
      False,
      False,
      False
    )

    note = {
      'created': datetime.fromtimestamp(int(data.created) / 1000).isoformat(),
      'updated': datetime.fromtimestamp(int(data.updated) / 1000).isoformat(),
      'title': data.title,
      'content_raw': data.content,
      'tags': [],
      'files': []
    }

    # get tags
    if data.tagGuids:
      for tagGuid in data.tagGuids:
        note['tags'].append(self.getTagName(tagGuid))

    # get files
    if data.resources:
      for resource in data.resources:
        note['files'].append(self.getResource(
          notebook,
          resource.guid
        ))

    return note

  def getTagName(self, guid):
    if not guid in self.tagMap:
      data = self.noteStore.getTag(self.token, guid)
      self.tagMap[guid] = data.name

    return self.tagMap[guid]

  def getResource(self, notebook, guid):
    data = self.noteStore.getResource(
      self.token,
      guid,
      True,
      False,
      True,
      False
    )
    if data.attributes.fileName:
      name = data.attributes.fileName
    else:
      ext = mimetypes.guess_extension(data.mime) if data.mime else ''
      if not ext: ext = ''

      name = data.guid + ext

    bucket = notebook + '/files'
    self.output.set(name, data.data.body, bucket=bucket)

    return bucket + '/' + name

  def writeCsvData(self, bucket, name, data):
    csvfile = self.output.getStream(name, bucket=bucket, mode='w')

    writer = csv.writer(csvfile, delimiter=';',
                            quotechar='"', quoting=csv.QUOTE_ALL)

    writer.writerow(data[0].keys())

    for note in data:
      note['tags'] = ','.join(note['tags'])
      note['files'] = ','.join(note['files'])

      writer.writerow(note.values())

  def runBackup(self):
    self.initClient()

    notebooks = self.noteStore.listNotebooks(self.token)

    for notebook in notebooks:
      self.progressHandler.startTask('Backing up notebook ' + notebook.name)

      filt = NoteFilter()
      filt.notebookGuid = notebook.guid
      notelist = self.noteStore.findNotes(self.token, filt, 0, 100)

      if not len(notelist.notes): continue

      notes = []

      self.progressHandler.startTask('Notebook: ' + notebook.name)

      i = 0
      for note in notelist.notes:
        i += 1
        notes.append(self.getNote(notebook.name, note.guid))

        self.progressHandler.setProgress(float(i) / len(notelist.notes))

      if self.add_note_files:
        for note in notes:
          filename = note['title'] + '.xml'
          self.output.set(filename, note['content_raw'],
            bucket=notebook.name + '/notes')

      if self.create_json:
        jsonData = json.dumps(notes)
        self.output.set('data.json', jsonData, bucket=notebook.name)

      if self.create_csv:
        self.writeCsvData(notebook.name, 'data.csv', notes)
