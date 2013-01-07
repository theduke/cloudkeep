
class Plugin(object):

  def __init__(self):
    self.config = {}
    self.logger = None
    self.progressHandler = None

    self.addConfig('name')

    self.setup()

  def getClassName(self):
    name = self.__class__.__module__ + '.' + self.__class__.__name__
    return name

  def setProgressHandler(self, handler):
    self.progressHandler = handler

  def setup(self):
    pass

  def addConfig(self, name, typ='string', default=None, description=''):
    types = ['string', 'number', 'int', 'float', 'bool']

    if not typ in types:
      raise Exception('Unknown config type: ' + typ)

    self.config[name] = {'typ': typ, 'default': default}
    self.__dict__[name] = default

  def validate(self):
    for name, conf in self.config.items():
      value = self.__dict__[name]

      if value == None:
        raise Exception('Required config field {name} is not set on {cl}'.format(
          name=name,
          cl=self.__class__.__name__
        ))

      valid = self.validateField(conf['typ'], value)

      if not valid:
        raise Exception('Config validation failed: field {name}, value {val}'.format(
          name=name,
          val=value
        ))

  def validateField(self, typ, value):
    valid = None

    if typ == 'string':
      valid = type(value) == str
    elif typ == 'numeric':
      valid = type(value) in [int, float]
    elif typ == 'int':
      valid = type(value) == int
    elif typ == 'float':
      valid = type(value) == float
    elif typ == 'bool':
      valid = type(value) == bool

    return valid

  def getConfig(self):
    config = dict(
      (name, self.__dict__[name]) for (name, conf) in self.config.items()
    )

    # remove name, should not be in save
    del config['name']

    return config

  def setConfig(self, data):
    for name, val in data.items():
      self.__dict__[name] = val

  def setLogger(self, logger):
    self.logger = logger

class ProgressHandler(object):
  def __init__(self):
    self.tasks = {}
    self.activeTask = None

  def addTask(self, name, active=True, progress=0):
    self.tasks[name] = progress

    self.onTaskAdded(name, progress)
    if active:
      self.activateTask(name)

  def activateTask(self, name):
    self.activeTask = name
    self.onTaskActivated(name, self.tasks[name])

  def setProgress(self, progress):
    self.tasks[self.activateTask] = progress

    self.onProgressChanged(self.activateTask, progress)

  def onTaskAdded(self, name, progress):
    # implement in child class
    pass

  def onTaskActivated(self, name, progress):
    # implement in child class
    pass

  def onProgressChanged(self, name, progress):
    # implement in child classes
    pass

