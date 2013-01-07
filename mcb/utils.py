from subprocess import *
import tarfile
import sys, os

def call(args):
  p = Popen(args, stdout=PIPE, stderr=PIPE)
  result = p.communicate()

  return (p.returncode, result[0], result[1])

def createArchive(path, compression, fileObject):
  """
  Create a tar archive, optionally compressed with gzip or bzip2.
  Add path to the tar file.

  Compression can be "bzip2" or "gzip"
  """
  mode = 'w'

  if compression:
    mode += ':' + compression

  tarFile = tarfile.open(mode=mode, fileobj= fileObject)
  os.chdir(os.path.dirname(path))
  tarFile.add(os.path.basename(path))
  tarFile.close()
