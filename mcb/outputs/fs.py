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

  def getPath(self, name, bucket=None, create=False):
    path = super(Filesystem, self).getPath(name, bucket)

    if create:
      parent = os.path.dirname(path)

      if not os.path.isdir(parent):
        os.makedirs(parent)

    return path

  def set(self, name, data, bucket=None, mode='w'):
    path = self.getPath(name, bucket, create=True)

    f = gzip.open(path, mode) if self.gzip else open(path, mode)

    f.write(data)
    f.close()

  def get(self, name, bucket=None):
    path = self.getPath(name, bucket, create=False)

    if os.path.isfile(path):
      f = open(path, 'r')
      return f.read()
    else:
      return False

  def getStream(self, name, bucket=None, mode='r+'):
    path = self.getPath(name, bucket, create=True)

    if not os.path.isfile(path):
      mode = 'w+'

    return open(path, mode)
