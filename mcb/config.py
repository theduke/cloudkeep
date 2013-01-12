import sys, os
import json
import yaml
from mcb.outputs import OutputPipe

class Config(object):

  def __init__(self):
    self.services = []
    self.outputs = []

    self.filepath = None

  def buildPlugin(self, conf):
    name = conf['className']

    moduleName = name[:name.rfind('.')]
    className = name[name.rfind('.')+1:]

    mod = __import__(moduleName, fromlist=[className])
    clas = getattr(mod, className)

    instance = clas()
    instance.setConfig(conf)

    return instance

  def addService(self, conf):
    self.services.append(conf)

  def getServices(self):
    return [self.buildPlugin(conf) for conf in self.services]

  def importServices(self, services):
    new = []

    for service in services:
      new.append(service.getConfig())

    self.services = new

  def addOutput(self, output):
    self.outputs.append(output)

  def getOutputs(self):
    return [self.buildPlugin(conf) for conf in self.outputs]

  def getOutputPipe(self):
    return OutputPipe(self.getOutputs())

  def importOutputs(self, outputs):
    new = []

    for output in outputs:
      new.append(output.getConfig())

    self.outputs = new

  def getAsDict(self):
    return {
      'services': self.services,
      'outputs': self.outputs
    }

  def save(self):
    if self.filepath: self.toFile()

  def fromDict(self, conf):
    if not 'services' in conf:
      raise Exception('Invalid config: no services data')
    if not 'outputs' in conf:
      raise Exception('Invalid config: no outputs data')

    self.services = conf['services']
    self.outputs = conf['outputs']

  def fromFile(self, path, format='yaml', create=True):
    self.filepath = path

    if not os.path.isfile(path) and create:
      return

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

    self.fromDict(conf)

  def toFile(self, path=None, format='yaml'):
    if not path: path = self.filepath

    conf = self.getAsDict()

    data = None
    if format == 'yaml':
      data = yaml.dump(conf, default_flow_style=False)
    elif format == 'json':
      data = json.dumps(conf)
    else:
      raise Exception('Invalid format: ' + format)

    f = open(path, 'w')
    f.write(data)
    f.close()
