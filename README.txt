mycloudbackup
=============

Back up data form all of your cloud services to a local or remote Filesystem (Dropbox, Amazon S3, ...)


Services
========

MyCloudBackup supports the following Services:

* Google Gmail - Back up all your Gmail mails into mbox files, does not preserv tags
* Google Calendar - Back up all your calendars as ical files

* Dropbox - Back up your entire Dropbox folder
* Email (Imap) - Back up any IMAP-accesible email account into widely used mbox files
* Github - Copy all your repositories and their issues

Outputs
=======

MyCloudBackup supports the following outputs (backup targets):

* Filesystem - Backup to your own computer

Soon to come:
* Dropbox
* Amazon S3
...

Dependencies
============

Required python packages:

* pyyaml - For config files (http://pyyaml.org)
* requests To ease working with various APIs(http://python-requests.org)

DropboxService:
* Dropbox python library: https://www.dropbox.com/developers/reference/sdk

GithubService:
* GitPython: https://github.com/gitpython-developers


===============================================================
To install all dependencies run bin/install-deps.py           =
Requires easy_install or pip                                  =
===============================================================
