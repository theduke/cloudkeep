import os, shutil

class Plugin(object):

  def __init__(self):
    self.config = []
    self.logger = None
    self.progressHandler = None

    self.addConfig('name', internal=True)

    self.setup()

  def getClassName(self):
    name = self.__class__.__module__ + '.' + self.__class__.__name__
    return name

  def setup(self):
    pass

  def getTmpPath(self):
    path = os.path.expanduser('~/.mcb/tmp/' + self.name)

    if os.path.isdir(path):
      shutil.rmtree(path)

    os.makedirs(path)
    return path

  def setProgressHandler(self, handler):
    self.progressHandler = handler

  def getConfig(self, name):
    config = None

    for conf in self.config:
      if conf['name'] == name:
        config = conf
        break

    return config

  def addConfig(self, name, typ='string', default=None, description='', internal=False):
    types = ['string', 'number', 'int', 'float', 'bool']

    if not typ in types:
      raise Exception('Unknown config type: ' + typ)

    self.config.append({
      'name': name,
      'typ': typ,
      'default': default,
      'description': description,
      'internal': internal
    })
    self.__dict__[name] = default

  def validate(self):
    for conf in self.config:
      name = conf['name']
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
      (conf['name'], self.__dict__[conf['name']]) for conf in self.config
    )

    # remove name, should not be in save
    del config['name']

    config['className'] = self.getClassName()

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

  def addTask(self, name, active=False, progress=0):
    self.tasks[name] = progress

    self.onTaskAdded(name, progress)
    if active:
      self.activateTask(name)

  def startTask(self, name):
    if not name in self.tasks:
      self.addTask(name)

    self.activeTask = name
    self.onTaskActivated(name, self.tasks[name])

  def setProgress(self, progress):
    self.tasks[self.activateTask] = progress

    self.onProgressChanged(self.activateTask, progress)

  def finishTask(self, name):
    self.onTaskFinished(name)

  def onTaskAdded(self, name, progress):
    # implement in child class
    pass

  def onTaskActivated(self, name, progress):
    # implement in child class
    pass

  def onProgressChanged(self, name, progress):
    # implement in child classes
    pass

  def onTaskFinished(self, name):
    # implement in child classes
    pass
