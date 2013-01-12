import logging, time

from mcb.outputs import OutputPipe
from mcb import ProgressHandler
from mcb.config import Config

class Runner(object):

  def __init__(self, config=None):
    self.services = []
    self.outputs = []
    self.mode = Config.MODE_MIRROR

    self.logger = logging.getLogger('mcb')

    if config:
      self.loadConfig(config)

    self.progressHandler = None

  def loadConfig(self, config):
    self.config = config

    self.services = config.getServices()
    self.outputs = config.getOutputs()
    self.mode = config.mode

  def saveConfig(self):
    self.config.importServices(self.services)
    self.config.importOutputs(self.outputs)

    self.config.save()

  def setProgressHandler(self, handler):
    self.progressHandler = handler

  def getOutputPrefix(self):
    if self.mode == Config.MODE_MIRROR:
      prefix = 'mirror'
    elif self.mode == Config.MODE_FULL:
      localtime   = time.localtime()
      prefix = 'full/' + time.strftime("%Y_%m_%d_%H_%M_%S", localtime)
    else:
      raise Exception("Unknown mode: " + self.mode)

    return prefix

  def run(self):
    if not len(self.outputs):
      raise Exception("No outputs configured")

    # create output pipe
    pipe = OutputPipe(self.outputs)
    pipe.setLogger(self.logger)
    pipe.prepare()

    outputPrefix = self.getOutputPrefix()

    self.logger.info('Backing up {count} services'.format(
      count=len(self.services)
    ))
    for service in self.services:
      self.logger.info('Backing up ' + service.name)

      self.progressHandler.startTask('Backing up ' + service.name)

      service.validate()

      prefix = outputPrefix + '/' + service.getOutputPrefix()
      pipe.setPrefix(prefix)
      service.setLogger(self.logger)
      service.setOutput(pipe)
      service.setProgressHandler(self.progressHandler)

      service.run()

      self.progressHandler.finishTask('Backing up ' + service.name)

    self.logger.info('All done')

    self.logger.info('Saving data...')
    self.saveConfig()


