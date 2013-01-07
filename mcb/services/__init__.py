from mcb import Plugin

class Service(Plugin):

  def __init__(self):
    super(Service, self).__init__()
    self.output = None

  def getOutputPrefix(self):
    raise Exception('getOutputPrefix not implemented in ' + self.name)

  def setOutput(self, output):
    self.output = output

  def run(self):
    if not self.logger:
      raise Exception('No logger set')
    if not self.progressHandler:
      raise Exception('No progressHandler set')
    if not self.output:
      raise Exception('No output set')

    self.runBackup()

  def runBackup(self):
    raise Exception('Run method not implemented in: ' + self.__class__.__name__)
