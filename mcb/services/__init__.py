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
    self.runBackup()

  def runBackup(self):
    raise Exception('Run method not implemented in: ' + self.__class__.__name__)


