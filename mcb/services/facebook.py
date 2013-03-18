import json
import os, time
import urllib

from mcb.services import Service
from mcb.utils.dropbo import DropboxMixin

import requests
from bs4 import BeautifulSoup

class FacebookService(Service):

  FACEBOOK_APP_ID = '143285549161847'
  FACEBOOK_APP_SECRET = '437cc0d39865ca0ada857471e47c333a'

  def setup(self):
    self.name = 'facebook'
    self.pretty_name = 'Facebook'
    self.enabled = False

    self.addConfig('username', 'Username')
    self.addConfig('password', 'Password')

    self.addConfig('token', 'Token', default='', internal=True)

    self.client = None

  def getId(self):
    return self.name + '_' + self.username

  def getPrettyId(self):
    return self.pretty_name + ' - ' + self.username

  def getPluginOutputPrefix(self):
    return self.username

  def initClient(self):
    if not self.token:
      self.getToken()

    self.client = facebook.GraphAPI(self.token)

  def login(self):
    session = requests.Session()

    r = session.get('http://facebook.com')
    soup = BeautifulSoup(r.text)

    data = {}

    form = soup.find('form', id='login_form')

    for inp in form.find_all('input', type='hidden'):
      data[inp.attrs['name']] = inp.attrs['value']

    data['email'] = self.username
    data['pass'] = self.password

    url = form.attrs['action']

    response = session.post(url, data)
    if not session.cookies.get('c_user'):
      raise Exception('Could not log in - check credentials')

    return session

  def getToken(self):
    self.logger.info('Acquiring FB auth token')

    session = self.login()

    perms = [
      "read_friendlists",
      "read_mailbox",
      "read_stream",
      "user_about_me",
      "user_activities",
      "user_birthday",
      "user_checkins",
      "user_education_history",
      "user_events",
      "user_groups",
      "user_hometown",
      "user_interests",
      "user_likes",
      "user_location",
      "user_notes",
      "user_photos",
      "user_questions",
      "user_relationships",
      "user_relationship_details",
      "user_religion_politics",
      "user_status",
      "user_subscriptions",
      "user_videos",
      "user_website"
    ]

    args = {
      "client_id": self.FACEBOOK_APP_ID,
      "redirect_uri": "https://www.facebook.com/connect/login_success.html",
      "scope": ','.join(perms),
      "response_type": "token"
    }

    path = "https://graph.facebook.com/oauth/authorize?" + urllib.urlencode(args)

    self.logger.info('Trying to authorize app at ' + path)

    r = session.get(path)

    # Check if we are already authorized and got a token
    if r.url.find(args['redirect_uri']) == 0:
      pass

    soup = BeautifulSoup(r.text)

    data = {}

    form = soup.find('form', id='uiserver_form')

    if not form:
      raise Exception('Could not find authentication form')

    for inp in form.find_all('input'):
      if inp.attrs['name'] == 'cancel_clicked': continue

      data[inp.attrs['name']] = inp.attrs['value']

    for inp in form.find_all('select'):
      data[inp.attrs['name']] = ''

    url = form.attrs['action']

    response = session.post(url, data)



  def runBackup(self):
    self.initClient()
