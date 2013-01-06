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

  def add(self, name, data):
    path = self.path + '/' + self.prefix
    if not os.path.isdir(path):
      os.makedirs(path)

    path += '/' + name

    f = gzip.open(path, 'wb') if self.gzip else open(path, 'w')

    if (data):
      f.write(data)

    return f
