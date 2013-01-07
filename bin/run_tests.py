#! /bin/env python

import sys, os
import yaml

# set up PYTHONPATH
path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libpath = path
sys.path.append(libpath)

import mcb
from mcb.config import Config
from mcb.runner import Runner
from mcb.frontends.cli import getCliRunner

config = mcb.config.Config()
data = yaml.load(open(path + '/tests/conf1.yaml'))
config.outputs = data['outputs']

SERVICES_TO_TEST=[
  #'mcb.services.github.GithubService',
  #'mcb.services.dropbo.DropboxService'
  #'mcb.services.email.EmailImapService',
  #'mcb.services.google.CalendarService',
  'mcb.services.google.GmailService'
]

for name, conf in data['services'].items():
  if name in SERVICES_TO_TEST:
    config.services = {name: conf}

    runner = getCliRunner(config)
    runner.run()
    #runner.saveConfig()

