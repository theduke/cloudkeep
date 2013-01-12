MyCloudBackup
=============

We use dozens of cloud services on a daily basis. Most of them are a wonderful
thing, making our lifes easier and bringing great functionality.

But should you trust these services with all your valued private data?
What if one of those services should go down, cease operations, or be hacked?

This program gets all of your precious data from  your cloud services, and
backs it up to a storage of your choice (your own hard drive, Dropbox, Amazon S3,
an FTP Server, ...) so you always have a backup if something happens.

You can select the services you use, and back them up to the storage of your
choice.

MCB works from the command line, and also has a GUI.


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
* FTP - Back up to a remote FTP server

Soon to come:
* Amazon S3
...

Installation
============

You can install MyCloudBackup by using setuptools easy_install or pip
Install setuptools: http://pypi.python.org/pypi/setuptools

sudo pip install mycloudbackup

Usage - GUI
===========

Just start the GUI with mcb-gui and enjoy.

Usage - CLI
===========

...

================================================================================

Development
===========

MCB is under the New BSD License (see LICENSE.txt).

Bug reports, suggestions and contributions are very welcome.
Development happens at https://github.com/theduke/mycloudbackup .

Dependencies
============

These will automaticall be installed by pip.

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
