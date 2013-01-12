
from mcb import Plugin

class Output(Plugin):

  def __init__(self):
    super(Output, self).__init__()
    self.prefix = ''

  # do all neccessary setup
  def prepare(self):
    pass

  def setPrefix(self, prefix):
    self.prefix = prefix

  # add a new data unit to the store
  # returns a file-like object that can be written to
  def set(self, name, data, bucket=None, mode='w'):
    raise Exception('add method not implemented')

  def get(self, name, bucket=None):
    raise Exception('get method not implemented in ' + self.getClassName())

  def getStream(self, name, bucket=None, mode='r+'):
    raise Exception('getStream method not implemented in ' + self.getClassName())

class FilePipe(object):

  def __init__(self):
    self.files = []

  def setFiles(self, files):
    self.files = files

  def addFile(self, f):
    self.files.append(f)

  def write(self, data):
    for f in self.files:
      f.write(data)

  def close(self):
    for f in self.files:
      f.close()

class OutputPipe(object):

  def __init__(self, outputs=[]):
    self.outputs = outputs

  def prepare(self):
    for output in self.outputs:
      output.prepare()

  def setLogger(self, logger):
    for output in self.outputs:
      output.setLogger(logger)

  def setPrefix(self, prefix):
    for output in self.outputs:
      output.setPrefix(prefix)

  def addOutput(self, output):
    self.outputs.push(output)

  def setOutputs(self, outputs):
    self.outputs = outputs

  def set(self, name, data, bucket=None, mode='w'):
    for output in self.outputs:
      f = output.set(name, data, bucket, mode)

  def get(self, name, bucket=None):
    return [output.get(name, bucket) for output in self.outputs]

  def getStream(self, name, bucket=None, mode='r+'):
    pipe = FilePipe()

    for output in self.outputs:
      f = output.getStream(name, bucket, mode)

      if not f:
        raise Exception('Could not open "{bucket}/{file}"" in mode {mode}'.format(
          bucket=bucket,
          file=name,
          mode=mode
        ))

      pipe.addFile(f)

    return pipe
