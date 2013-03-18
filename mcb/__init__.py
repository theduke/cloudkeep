import os, shutil

from pprint import pprint

class Plugin(object):

  TYPE_BOOL = 'bool'
  TYPE_STRING = 'string'
  TYPE_NUMBER = 'number'
  TYPE_INT = 'int'
  TYPE_FLOAT = 'float'

  def __init__(self):
    self.enabled = True
    self.config = []
    self.logger = None
    self.progressHandler = None

    self.addConfig('name', 'Name', internal=True)
    self.addConfig('pretty_name', 'Pretty Name', internal=True)

    self.setup()

  def getClassName(self):
    name = self.__class__.__module__ + '.' + self.__class__.__name__
    return name

  def getId(self):
    raise Exception('getId() not implemented in ' + self.getClassName())

  def getPrettyId(self):
    raise Exception('getPrettyId() not implemented in ' + self.getClassName())

  def setup(self):
    pass

  def getTmpPath(self, create=True):
    path = os.path.expanduser('~/.mcb/tmp/' + self.name)
    
    if create:
      if os.path.isdir(path):
        shutil.rmtree(path)
      os.makedirs(path)

    return path
    
  def setProgressHandler(self, handler):
    self.progressHandler = handler

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
    
    # if this value is allowed to be empty (default is set)
    # and it is an empty string, it is valid
    if value == '' and item['default'] != None:
        return True

    if item['options'] and not (value in item['options'].keys()):
      return False

    if typ == self.TYPE_STRING:
      valid = type(value) == str and len(value) > 0
    elif typ == self.TYPE_NUMBER:
      valid = value.replace('.','',1).isdigit() if type(value) == str else (type(value) in [int, float])
    elif typ == self.TYPE_INT:
      valid = value.isdigit() if type(value) == str else (type(value) == int)
    elif typ == self.TYPE_FLOAT:
      valid = value.replace('.','',1).isdigit() if type(value) == str else (type(value) == float)
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
      config_item = self.getConfigItem(name)

      # If no proper value is given and default is avail, use that
      valid = self.validateField(config_item, val)
      if not valid and config_item['default'] != None:
        val = config_item['default'
        ]
      self.__dict__[name] = val

  def setLogger(self, logger):
    self.logger = logger

class ProgressHandler(object):

  def __init__(self):
    self.tasks = {}
    self.activeTask = None
    
  def showPrompt(self, msg, exceptInput=False):
    raise Exception('showPrompt not implemented')

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

  def getFinishedTasks(self):
    finished = [value for name, value in self.tasks.items() if value == 100]
    return finished

  def getTaskProgress(self):
    return len(self.getFinishedTasks()) / float(len(self.tasks))

  def finishTask(self, name):
    if not name in self.tasks:
      raise Exception("Task " + name + " does not exist")

    self.tasks[name] = 100
    self.onTaskFinished(name, self.getTaskProgress())

  def finishBackup(self):
    """Call this when the runner is done."""

    self.onBackupFinished()

  def onTaskAdded(self, name, progress):
    # implement in child class
    pass

  def onTaskActivated(self, name, progress):
    # implement in child class
    pass

  def onProgressChanged(self, name, progress):
    # implement in child classes
    pass

  def onTaskFinished(self, name, tasks_progress):
    # implement in child classes
    pass

  def onBackupFinished(self):
    # implement in child classes
    pass
