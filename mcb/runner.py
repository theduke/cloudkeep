import logging
from mcb.outputs import OutputPipe
from mcb import ProgressHandler

class Runner(object):

  def __init__(self, config=None):
    self.services = []
    self.outputs = []

    logging.basicConfig(level=logging.DEBUG)
    self.logger = logging.getLogger('mcb')

    if config:
      self.loadConfig(config)

    self.progressHandler = None

  def loadConfig(self, config):
    self.config = config

    self.services = config.getServices()
    self.outputs = config.getOutputs()

  def saveConfig(self):
    self.config.importServices(self.services)
    self.config.importOutputs(self.outputs)

    self.config.save()

  def setProgressHandler(self, handler):
    self.progressHandler = handler

  def run(self):
    # create output pipe
    pipe = OutputPipe(self.outputs)
    pipe.prepare()
    pipe.setLogger(self.logger)

    self.logger.info('Backing up {count} services'.format(
      count=len(self.services)
    ))
    for service in self.services:
      self.logger.info('Backing up ' + service.__class__.__name__)

      service.validate()

      pipe.setPrefix(service.getOutputPrefix())
      service.setLogger(self.logger)
      service.setOutput(pipe)
      service.setProgressHandler(self.progressHandler)

      service.run()

    self.logger.info('All done')

    self.logger.info('Saving data...')
    self.saveConfig()


