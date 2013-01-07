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

    self.addConfig('username', default='')
    self.addConfig('password', default='')

    self.addConfig('user', default='')
    self.addConfig('mirror_repos', 'bool', default=True)

    self.addConfig('compress_repos', default=False, description="""
Compress the repository into a tar archive, with optional bzip2/gzip compression.
Compression is required for non FileSystem outputs.
Options: [none, tar, gz, bz2]
""")

  def getPluginOutputPrefix(self):
    return self.username

  def getRepos(self):
    url = self.apiUrl + '/users/' + self.username + '/repos'
    r = requests.get(url, auth=(self.username, self.password))
    repos = json.loads(r.text)

    return repos

  def checkForGit(self):
    if call(['git', '-h'])[0] != 0:
      raise Exception('Git command is not in path')

  def mirrorRepo(self, name, url):
    """
    Mirror a repo.
    Note that only the FileSystem output supports non-compressed mode.
    """

    if self.compress_repos:
      # glone the git repo


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

  def runBackup(self):
    self.tmpPath = self.getTmpPath()
    for repo in self.getRepos():
      if self.mirror_repos:
        self.mirrorRepo(repo['name'], repo['git_url'])
