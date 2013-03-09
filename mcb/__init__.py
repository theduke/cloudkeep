import os, shutil

class Plugin(object):

  TYPE_BOOL = 'bool'
  TYPE_STRING = 'string'
  TYPE_NUMBER = 'number'
  TYPE_INT = 'int'
  TYPE_FLOAT = 'float'

  def __init__(self):
    self.config = []
    self.logger = None
    self.progressHandler = None

    self.addConfig('name', 'Name', internal=True)
    self.addConfig('pretty_name', 'Pretty Name', internal=True)

    self.addConfig('id', 'Id', description="""Set an name to identify this account.""", default='auto')

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

  def getConfigValue(self, name, injectDefault=False):
    val = self.__dict__[name]
    item = self.getConfigItem(name)

    if not val and injectDefault and item['default']:
      val = item['default']

    return val

  def setConfigValue(self, name, value):
    self.__dict__[name] = value

  def addConfig(self, name, pretty_name, typ='string', default=None, description='', internal=False, options=None):
    """
    Set up a new config field.
    typ can be one of the mcb.Plugin.TYPE_* values.

    Internal config values are not set by the user manually but by the plugin.
    This could be an API token acquired.

    If the value should only be one of a list of options, set options 
    to an dict with identifiers as keys and pretty names as values. 
    The plugin will only validate if the value is on of those.
    """
    types = [
      self.TYPE_STRING, 
      self.TYPE_NUMBER, 
      self.TYPE_INT, 
      self.TYPE_FLOAT, 
      self.TYPE_BOOL
    ]

    if not typ in types:
      raise Exception('Unknown config type: ' + typ)

    self.config.append({
      'name': name,
      'pretty_name': pretty_name,
      'typ': typ,
      'default': default,
      'description': description,
      'internal': internal,
      'options': options
    })
    self.__dict__[name] = default

  def validate(self, raiseException=True):
    errors = []

    for conf in self.config:
      name = conf['name']
      value = self.__dict__[name]

      if value == None:
        raise Exception('Required config field {name} is not set on {cl}'.format(
          name=name,
          cl=self.__class__.__name__
        ))

      valid = self.validateField(conf, value)

      if not valid:
        if raiseException:
          raise Exception('Config validation failed: field {name}, value {val}'.format(
            name=name,
            val=value
          ))
        else:
          errors.append(name)

      return errors

  def validateField(self, item, value):
    valid = None
    typ = item['typ']

    if item['options'] and not (value in item['options'].keys()):
      return False

    if typ == self.TYPE_STRING:
      valid = type(value) == str
    elif typ == self.TYPE_NUMBER:
      valid = type(value) in [int, float]
    elif typ == self.TYPE_INT:
      valid = type(value) == int
    elif typ == self.TYPE_FLOAT:
      valid = type(value) == float
    elif typ == self.TYPE_BOOL:
      valid = type(value) == bool

    return valid

  def getConfigItem(self, name):
    for item in self.config:
      if item['name'] == name:
        return item

    return None

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
    self.tasks[self.activeTask] = progress

    self.onProgressChanged(self.activeTask, progress)

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
