#! /usr/bin/env python

from distutils.core import setup

setup(
    name='MyCloudBackup',
    version='0.1dev',
    author='Christoph Herzog',
    author_email='chris@theduke.at',
    license='New BSD License',
    url='http://pypi.python.org/pypi/TowelStuff/',
    packages=['mcb',],
    scripts=['bin/run_tests.py'],
    description="Back up data the cloud services you use",
    long_description=open('README.txt').read(),
    install_requires=[
       #"Django >= 1.1.1",
        "pyyaml",
        "requests",
        "dropbox", # for DropboxService
        "gitpython" #for GithubService
    ],
)
