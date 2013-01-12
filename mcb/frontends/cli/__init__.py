
import argparse, sys, os
import logging

from mcb.runner import Runner
from mcb import ProgressHandler, utils
from mcb.config import Config

class CliProgressHandler(ProgressHandler):

  def onTaskAdded(self, name, progress):
    pass

  def onTaskActivated(self, name, progress):
    print("Starting task: " + name)

  def onProgressChanged(self, name, progress):
    # implement in child classes
    pass

  def onTaskFinished(self, name):
    print("Finished task: " + name)


class Cli(object):

  def __init__(self):
    pass

  def getParser(self):
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', default='~/.mycloudbackup', help="Config file to use")
    parser.add_argument('-v', '--verbose', action='store_true')

    subparsers = parser.add_subparsers(title='commands')

    #############
    #ADD SERVICE
    #############

    addService = subparsers.add_parser('add-service',
      help='Add a new service to be backed up.'
    )

    help = "Type of the service, available: "
    help += '[' +  '|'.join(utils.getAllServices().keys())
    addService.add_argument('--type', help=help)

    addService.set_defaults(func=self.addServiceCmd)

    #############
    # RUN
    #############

    run = subparsers.add_parser('run',
      help='Run the backups.'
    )
    run.set_defaults(func=self.runCmd)

    return parser

  def prompt(self, msg, validate=None, default=None):

    if validate == 'bool':
      msg += ' [yes/no]'
    elif type(validate) == list:
      msg += ' [' + ','.join(validate) + ']'

    if default is not None:
      defMsg = None

      if type(default) == bool:
        defMsg = 'yes' if default else 'no'
      elif type(default) == str:
        defMsg = default if len(default) else '""'
      else:
        default

      msg += ' [default: {d}]'.format(d=defMsg)

    msg += ': '

    result = raw_input(msg)

    # if nothing entered, and default is set, we can skip the rest
    if not result and default is not None:
      return default

    if validate:
      valid = True

      if validate == 'string':
        valid = len(result) > 0
      elif validate in ['number', 'int', 'float']:
        valid = utils.is_number(result)
      elif validate == 'bool':
        if result == 'yes':
          result = True
        elif result == 'no':
          result = False
        else:
          valid = False
      elif type(validate) == list:
        valid = result in validate
      else:
        raise Exception("Unknown validation type " + validation)

    if not valid:
      return self.prompt(msg, validate)
    else:
      return result

  def error(self, msg):
    print("Error: " + msg)
    sys.exit(1)

  def getConfig(self, path):
    path = os.path.expanduser(path)

    config = Config()
    config.fromFile(path)

    return config

  def addServiceCmd(self, args):
    services = utils.getAllServices()

    if not args.type:
      args.type = self.prompt('Choose service type', services.keys())

    if not args.type in services:
      self.error('Unknown service type: ' + args.type)

    service = services[args.type]()

    serviceConfig = {}

    for conf in service.config:
      if conf['internal']: continue

      name = conf['name']

      val = None
      if not val:
        msg = '{name} ({help})'.format(name=name, help=conf['description'])
        val = self.prompt(msg, conf['typ'], conf['default'])

      serviceConfig[name] = val

    config = self.getConfig(args.config)

    serviceConfig['className'] = service.getClassName()
    config.addService(serviceConfig)

    config.toFile()

    print("Service added successfully")

  def getCliRunner(self, config):
    handler = CliProgressHandler()

    runner = Runner(config)
    runner.setProgressHandler(handler)

    return runner

  def runCmd(self, args):
    if args.verbose:
      logging.basicConfig(level=logging.DEBUG)

    config = self.getConfig(args.config)
    runner = self.getCliRunner(config)

    print("Runnin all backups")
    runner.run()
    print("All backups finished")

  def run(self, args):
    parser = self.getParser()
    args = parser.parse_args(args)
    args.func(args)

if __name__ == '__main__':
  args = ['add-service']

  cli = Cli()
  cli.run(args)
