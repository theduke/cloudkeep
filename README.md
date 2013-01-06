mycloudbackup
=============

Back up data form all of your cloud services to a local or remote Filesystem (Dropbox, Amazon S3, ...)


Services
========

MyCloudBackup supports the following Services:

* Google Calendar - Back up all your calendars as ical files
* Dropbox - Back up your entire Dropbox folder
* Email (Imap) - Back up any IMAP-accesible email account into widely used mbox files

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

* pyyaml
* requests

Dropbox API:
https://www.dropbox.com/developers/reference/sdk
https://www.dropbox.com/static/developers/dropbox-python-sdk-1.5.1.zip
