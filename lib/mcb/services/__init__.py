from mcb import Plugin

class Service(Plugin):

  def __init__(self):
    super(Service, self).__init__()
    self.output = None

  def getOutputPrefix(self):
    return self.name

  def setOutput(self, output):
    self.output = output

  def runBackup(self):
    raise Exception('Run method not implemented in: ' + self.__class__.__name__)


