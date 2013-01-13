
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
    print("Progress: {p}%".format(p=int(progress*100)))

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
    # add-service
    #############

    addService = subparsers.add_parser('add-service',
      help='Add a new service to be backed up'
    )

    help = "Type of the service, available: "
    help += '[' +  '|'.join(utils.getAllServices().keys())
    addService.add_argument('--type', help=help)

    addService.set_defaults(func=self.addServiceCmd)

    #############
    # add-output
    #############

    addOutput = subparsers.add_parser('add-output',
      help='Add a new output'
    )

    help = "Type of the output, available: "
    help += '[' +  '|'.join(utils.getAllOutputs().keys())
    addOutput.add_argument('--type', help=help)

    addOutput.set_defaults(func=self.addOutputCmd)

    #############
    # RUN
    #############

    run = subparsers.add_parser('run',
      help='Run the backups'
    )

    help = "Backup mode: [mirror, full]"
    run.add_argument('--mode', help=help)

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
        defMsg = default

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
    self.addPluginConfig('service', args)

  def addOutputCmd(self, args):
    self.addPluginConfig('output', args)

  def addPluginConfig(self, pluginType, args):
    """
    Helper function for adding an output or a service to the config.
    pluginType is either "service" or "output"
    """

    config = self.getConfig(args.config)

    method = getattr(utils, 'getAll' + pluginType.capitalize() + 's')
    items = method()

    if not args.type:
      args.type = self.prompt('Choose ' + pluginType + ' type', items.keys())

    if not args.type in items:
      self.error('Unknown ' + pluginType + ' type: ' + args.type)

    plugin = items[args.type]()

    pluginConfig = {}

    for conf in plugin.config:
      if conf['internal']: continue

      name = conf['name']

      val = None
      if not val:
        msg = '{name} ({help})'.format(name=name, help=conf['description'])
        val = self.prompt(msg, conf['typ'], conf['default'])

      pluginConfig[name] = val

    if pluginConfig['id'] == 'auto':
      id = plugin.name + '_' + str(len(getattr(config, pluginType + 's')))
      pluginConfig['id'] = id

    pluginConfig['className'] = plugin.getClassName()

    method = getattr(config, 'add' + pluginType.capitalize())
    method(pluginConfig)

    config.toFile()

    print(pluginType.capitalize() + " added successfully")

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

    if args.mode:
      runner.mode = args.mode

    print("Runnin all backups")

    if args.verbose:
      runner.run()
    else:
      try:
        runner.run()
      except Exception as e:
        if args.verbose:
          raise e
        else:
          print("An error occured: " + e.message)

        sys.exit(1)

    print("All backups finished")

  def run(self, args):
    parser = self.getParser()
    args = parser.parse_args(args)
    args.func(args)

if __name__ == '__main__':
  args = ['add-service']

  cli = Cli()
  cli.run(args)
