import os
import gzip
from mcb.outputs import Output

class Filesystem(Output):

  def setup(self):
    self.name = 'filesystem'

    self.addConfig('path')
    self.addConfig('gzip', 'bool', False)

  def prepare(self):
    pass

  def set(self, name, data, bucket=None, mode='w'):
    path = self.path + os.path.sep  + self.prefix

    if bucket:
      path += os.path.sep + bucket

    if not os.path.isdir(path):
      os.makedirs(path)

    path += os.path.sep + name

    f = gzip.open(path, mode) if self.gzip else open(path, mode)

    f.write(data)
    f.close()

  def get(self, name, bucket=None):
    path = self.path + os.path.sep  + self.prefix

    if bucket:
      path += os.path.sep + bucket

    path += os.path.sep + name

    if os.path.isfile(path):
      f = open(path, 'r')
      return f.read()
    else:
      return False

  def getStream(self, name, bucket=None, mode='r+'):
    path = self.path + os.path.sep  + self.prefix

    if bucket:
      path += os.path.sep + bucket

    if not os.path.isdir(path):
      os.makedirs(path)

    path += os.path.sep + name

    if not os.path.isfile(path):
      mode = 'w+'

    return open(path, mode)
