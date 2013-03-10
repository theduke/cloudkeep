import json, os
from pprint import pprint

from mcb.services import Service
from mcb.utils import call, createArchive

import requests

class GithubService(Service):
  """
  Mirror all your github repositories.
  Back up issue queues as CSV.
  """

  apiUrl = 'https://api.github.com'

  def setup(self):
    self.name = 'github'
    self.pretty_name = 'Github'

    self.addConfig('username', 'Username', default='')
    self.addConfig('password', 'Password', default='')

    self.addConfig('user', 'User', default='')

    self.addConfig('mirror_repos', 'Mirror repositories', 'bool', default=True)
    self.addConfig('compress_repos', 'Compress repos', default=False, options={
        'none': 'None',
        'gzip': 'GZIP',
        'bz2': 'bz2'
      }, description="""
Compress the repository into a tar archive, with optional bzip2/gzip compression.
Compression is required for non FileSystem outputs.
Options: [none, tar, gz, bz2]
""")

    self.addConfig('issues', 'Issues', 'bool', default=True)
    self.addConfig('user_repos', 'User repositories', default='', description="""By default, all repos of the user are mirrored. Specify a comma-separated list if you want to limit it to certain ones.""")


  def getId(self):
    return self.name + '_' + self.username

  def getPrettyId(self):
    return self.pretty_name + ' - ' + self.username
    
  def getPluginOutputPrefix(self):
    return self.username

  def doRequest(self, path, decode=True):
    url = self.apiUrl + path
    r = requests.get(url, auth=(self.username, self.password))

    return json.loads(r.text) if decode else r.text

  def getRepos(self):
    return self.doRequest('/users/' + self.username + '/repos')

  def checkForGit(self):
    if call(['git', '-h'])[0] != 0:
      raise Exception('Git command is not in path')

  def mirrorRepo(self, name, url):
    """
    Mirror a repo.
    Note that only the FileSystem output supports non-compressed mode.
    """

    if not self.compress_repos:
      raise Exception("Non-compressed mode not implemented yet")

    # clone the git repo

    path = self.tmpPath + os.path.sep + name + '.git'

    self.logger.debug('Cloning git repo {url} to {path}'.format(
      url=url, path=path
    ))
    result = call(['git', 'clone', '--mirror', url, path])

    if result[0] != 0:
      raise Exception('Could not clone {repo}: {o}'.format(
        repo=url, o=result[1] + "\n\n" + result[2]
      ))

    # create archive and write it
    self.logger.debug('Compressing repo into archive...')

    fileName = name + '.git.tar'

    if self.compress_repos != 'tar': fileName += '.' + self.compress_repos
    compression = self.compress_repos if self.compress_repos != 'tar' else None

    fileObject = self.output.getStream(fileName, name, 'w')
    createArchive(path, compression, fileObject)
    fileObject.close()

  def saveIssues(self, name):
    path = '/repos/theduke/' + name + '/issues'
    data = self.doRequest(path, decode=False)

    self.output.set('issues.json', data, bucket=name)

  def runBackup(self):
    self.tmpPath = self.getTmpPath()

    allowedRepos = self.user_repos.split(',') if self.user_repos else None

    for repo in self.getRepos():
      # if repos are limited to user_repos, skip as neccessary
      if allowedRepos and repo['name'] not in allowedRepos:
        continue

      if self.mirror_repos:
        self.mirrorRepo(repo['name'], repo['git_url'])

        if repo['has_issues']:
          self.saveIssues(repo['name'])
