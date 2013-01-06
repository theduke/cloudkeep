#! /bin/env python

import sys, os

# set up PYTHONPATH
path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
libpath = path
sys.path.append(libpath)

import mcb
from mcb.config import Config
from mcb.runner import Runner

config = mcb.config.Config()
config.fromFile(path + '/tests/conf1.yaml', 'yaml')

runner = Runner(config)
runner.run()
runner.saveConfig()

