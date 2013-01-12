MyCloudBackup
=============

Back up data from all of your cloud services to a local or remote storate(like
Filesystem, Amazon S3, Dropbox, ...).

MCB works from the command line, and also has a GUI.

MCB is under the New BSD License (see LICENSE.txt).

Bug reports, suggestions and contributions are very welcome.
Development happens at https://github.com/theduke/mycloudbackup .


Services
========

MyCloudBackup supports the following cloud services:

* Google Gmail - Back up all your Gmail mails into mbox files, does not preserv tags
* Google Calendar - Back up all your calendars as ical files

* Dropbox - Back up your entire Dropbox folder
* Email (Imap) - Back up any IMAP-accesible email account into widely used mbox files
* Github - Copy all your repositories and their issues

Outputs
=======

MyCloudBackup supports the following outputs (backup targets):

* Filesystem - Backup to your own computer
* Dropbox - Back up to your Dropbox account

Soon to come:
* Amazon S3
...

Installation
============

You can install MyCloudBackup by using setuptools easy_install or pip
Install setuptools: http://pypi.python.org/pypi/setuptools

sudo pip install mycloudbackup

Dependencies
============

Required python packages:

* pyyaml - For config files (http://pyyaml.org)
* requests To ease working with various APIs(http://python-requests.org)

DropboxService:
* Dropbox python library: https://www.dropbox.com/developers/reference/sdk

GithubService:
* GitPython: https://github.com/gitpython-developers

Plugin System
=============

MCB has a modular plugin system, that makes it easy to add new services and
outputs.

Will write documentation on how to write plugins soon.
For now, just copy an existing one and adapt it.

Starting point for services: mcb/services/github.py
               for outputs:  mcb/outputs/dropbox.py

Contributors
============

Christoph Herzog - chris@theduke.at
