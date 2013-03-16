import os
import gzip
import StringIO
import ftplib

from mcb.outputs import Output, FakeFile

class FtpOutput(Output):

  def setup(self):
    self.name = 'ftp'
    self.pretty_name = 'FTP'

    self.addConfig('host', 'Host')
    self.addConfig('port', 'Port', 'int', default=21)
    self.addConfig('ssl', 'SSL', 'bool', default=False)
    self.addConfig('username', 'Username', default=None)
    self.addConfig('password', 'Password', default='')

    self.addConfig('path', 'Path', description="The path on the server where backups should be stored")

    self.ftp = None

  def getId(self):
    return self.name + '_' + host

  def getPrettyId(self):
    return self.pretty_name + ' - ' + self.host

  def prepare(self):
    self.connect()

  def getPath(self, name, bucket=None, create=False):
    path = self.path + os.path.sep + super(FtpOutput, self).getPath(name, bucket)

    if create:
      parent = os.path.dirname(path)

      if not self.isdir(parent):
        self.makedirs(parent)

    return path

  def connect(self):
    ftp = ftplib.FTP_TLS() if self.ssl else ftplib.FTP()

    ftp.connect(self.host, self.port)

    if self.username:
      ftp.login(self.username, self.password)
    else:
      ftp.login()

    if self.ssl:
      ftp.prot_p()

    self.ftp = ftp

  def isdir(self, path):
    try:
      self.ftp.cwd(path)
      return True
    except ftplib.error_perm:
      return False

  def isfile(self, path):
    files = []
    def write(line):
      files.append(line)

    if self.isdir(os.path.dirname(path)):
      self.ftp.retrlines('NLST', write)

    return os.path.basename(path) in files

  def makedirs(self, path):
    parent = os.path.dirname(path)
    if not self.isdir(parent):
      self.makedirs(parent)

    self.ftp.mkd(path)

  def download(self, path):
    path = os.path.dirname(path)
    name = os.path.basename(path)

    tmpPath = self.tmpPath + os.path.sep + name
    fileObj = open(tmpPath, 'w+b')

    self.ftp.cwd(path)
    self.ftp.retrbinary('RETR ' + name, fileObj.write)

    fileObj.seek(0)
    return fileObj

  def set(self, name, data, bucket=None, mode='w'):
    path = self.getPath(name, bucket, create=True)

    self.ftp.cwd(os.path.dirname(path))

    fileObj = data if hasattr(data, 'read') else StringIO.StringIO(data)
    self.ftp.storbinary('STOR ' + name, fileObj)

  def get(self, name, bucket=None):
    path = self.getPath(name, bucket, create=False)
    return self.download(path).read() if self.isfile(path) else False

  def getStream(self, name, bucket=None, mode='r+'):
    path = self.getPath(name, bucket, create=True)

    mode = mode.replace('b', '')

    if mode == 'r':
      return self.download(path)
    else:
      return FakeFile(name, bucket, mode, self, self.tmpPath)
