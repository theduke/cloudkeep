
from mcb.runner import Runner
from mcb import ProgressHandler

class CliProgressHandler(ProgressHandler):
  pass

def getCliRunner(config):
  handler = CliProgressHandler()

  runner = Runner(config)
  runner.setProgressHandler(handler)

  return runner
