
class Plugin(object):

  def __init__(self):
    self.config = {}
    self.logger = None

    self.addConfig('name')

    self.setup()

  def getClassName(self):
    name = self.__class__.__module__ + '.' + self.__class__.__name__
    return name

  def setup(self):
    pass

  def addConfig(self, name, typ='string', default=None):
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
    return config

  def setConfig(self, data):
    for name, val in data.items():
      self.__dict__[name] = val

  def setLogger(self, logger):
    self.logger = logger
