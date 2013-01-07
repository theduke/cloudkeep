from mcb.services import Service
from mcb.services.email import EmailImapService

import requests
from bs4 import BeautifulSoup

class GoogleHack(Service):

  loginUrl = 'https://accounts.google.com/ServiceLogin'

  def __init__(self):
    super(GoogleHack, self).__init__()
    self.addConfig('email')
    self.addConfig('password')

  def login(self):
    self.session = session = requests.Session()
    response = session.get(self.loginUrl)

    soup = BeautifulSoup(response.text)

    data = {}

    form = soup.find('form', id='gaia_loginform')

    for inp in form.find_all('input', type='hidden'):
      data[inp.attrs['name']] = inp.attrs['value']

    data['Email'] = self.email
    data['Passwd'] = self.password

    url = form.attrs['action']

    response = session.post(url, data)

    if not response.text.find('Connected accounts'):
      raise Exception('Login failed')


class CalendarService(GoogleHack):

  exportUrl = 'https://www.google.com/calendar/exporticalzip'

  def setup(self):
    self.name = 'google.calendar'

  def getOutputPrefix(self):
    return 'google.calendar.' + self.email.replace('@', '_at_')

  def runBackup(self):
    self.login()
    response = self.session.get(self.exportUrl)
    self.output.set('calendars.zip', response.content)

class GmailService(EmailImapService):
  """Imap imported customized for Gmail, to prevent duplicate messages
  A lot more coud be done here, this is just preliminary:
  Problem: Gmail supplies each tag as a separate IMAP folder, so messages
  get duplicated multiple times.

  For now we just use the [Gmail]/All folder
  This does not allow to restore the tag structure properly though!
  """

  def setup(self):
    super(GmailService, self).setup()

    self.name = 'google.gmail'

    self.host = 'imap.gmail.com'
    self.port = 993
    self.ssl = True

  def getFolders(self):
    return ['[Gmail]/All Mail']
