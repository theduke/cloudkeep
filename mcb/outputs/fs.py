import os
import gzip
from mcb.outputs import Output

class Filesystem(Output):

  def setup(self):
    self.name = 'filesystem'
    self.pretty_name = 'Filesystem'

    self.addConfig('path', 'Path')
    self.addConfig('gzip', 'GZIP', 'bool', False)

  def getId(self):
    return self.name + '_' + self.path

  def getPrettyId(self):
    return self.pretty_name + ' - ' + self.path

  def prepare(self):
    pass

  def getPath(self, name, bucket=None, create=False):
    path = self.path + os.path.sep + super(Filesystem, self).getPath(name, bucket)

    if create:
      parent = os.path.dirname(path)

      if not os.path.isdir(parent):
        os.makedirs(parent)

    return path
  
  def createBucket(self, name):
    path = os.path.join(self.path, self.prefix, name)
    
    if not os.path.isdir(path):
      os.makedirs(path)

  def set(self, name, data, bucket=None, mode='w'):
    path = self.getPath(name, bucket, create=True)

    if hasattr(data, 'read'):
      data = data.read()

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
