
import json
import yaml
from mcb.outputs import OutputPipe

class Config(object):

  def __init__(self):
    self.services = {}
    self.outputs = {}

  def buildPlugin(self, name, conf):
    moduleName = name[:name.rfind('.')]
    className = name[name.rfind('.')+1:]

    mod = __import__(moduleName, fromlist=[className])
    clas = getattr(mod, className)

    instance = clas()
    instance.setConfig(conf)

    return instance

  def getServices(self):
    return [self.buildPlugin(name, conf) for name, conf in self.services.items()]

  # build an output instance from an OutputConfig
  def buildOutput(self, config):
    pass

  def getOutputs(self):
    return [self.buildPlugin(name, conf) for (name, conf) in self.outputs.items()]

  def getOutputPipe(self):
    return OutputPipe(self.getOutputs())

  def getAsDict(self):
    return {
      'services': self.services,
      'outputs': self.outputs
    }

  def fromFile(self, path, format='yaml'):
    f = open(path, 'r')
    data = f.read()
    f.close()

    conf = None

    if format == 'yaml':
      conf = yaml.load(data)
    elif format == 'json':
      conf = json.load(data)
    else:
      raise Exception('Invalid format: ' + format)

    if not 'services' in conf:
      raise Exception('Invalid config: no services data')
    if not 'outputs' in conf:
      raise Exception('Invalid config: no outputs data')

    self.services = conf['services']
    self.outputs = conf['outputs']

  def toFile(self, path, format='yaml'):
    conf = self.getAsDict()

    data = None
    if format == 'yaml':
      data = yaml.dump(data)
    elif format == 'json':
      data = json.dumps(data)
    else:
      raise Exception('Invalid format: ' + format)

    f = open(path, 'w')
    f.write(data)
    f.close()
