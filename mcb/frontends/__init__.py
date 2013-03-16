
import os

from mcb.runner import Runner
from mcb import ProgressHandler
from mcb.config import Config

class Frontend(object):

	def getConfig(self, path):
	    path = os.path.expanduser(path)

	    config = Config()
	    config.fromFile(path)

	    return config

def getCliRunner(config):
  handler = CliProgressHandler()

  runner = Runner(config)
  runner.setProgressHandler(handler)

