
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
  def add(self, name, data=None):
    raise Exception('add method not implemented')

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

  def add(self, name, data=None):
    for output in self.outputs:
      output.add(name, data)

