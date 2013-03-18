import os

try:
  # python 2
  import StringIO
except:
  # python 3
  import io
  from io import StringIO

  file = io.TextIOBase

from mcb import Plugin

class FakeFile(file):

  def __init__(self, name, bucket, mode, output, tmpPath):
    localPath = tmpPath + '/' + (bucket + name).replace('/', '_')

    super(FakeFile, self).__init__(localPath, 'w+b')

    if mode not in ['w', 'w+']:
      # we have to download the dropbox file first
      remoteFile = output.getStream(name, bucket, 'r')
      chunk = 10000
      while True:
        data = remoteFile.read(chunk)
        if not data:
          break
        self.write(data)

      # now we have to seek to the right position, depending on mode
      if mode == 'r+':
        self.seek(0)
      elif mode in ['a', 'a+']:
        self.seek(0, 2)
      else:
        raise Exception('Unknown mode: {m}'.format(m=mode))

    self.outputName = name
    self.outputBucket = bucket
    self.output = output

  def close(self):
    self.flush()
    self.seek(0, 0)
    self.output.set(self.outputName, self, bucket=self.outputBucket)
    super(FakeFile, self).close()


class Output(Plugin):

  def __init__(self):
    super(Output, self).__init__()
    self.prefix = ''

    self.tmpPath = self.getTmpPath()

  # do all neccessary setup
  def prepare(self):
    pass

  def setPrefix(self, prefix):
    self.prefix = prefix

  def getPath(self, name, bucket=None, sep=os.path.sep):
    path = self.prefix

    if bucket:
      path += sep + bucket

    path += sep + name

    return path
  
  def createBucket(self, name):
    raise Exception('createBucket not implemented')
  
  # add a new data unit to the store
  # returns a file-like object that can be written to
  def set(self, name, data, bucket=None, mode='w'):
    raise Exception('add method not implemented')
  
  def setFromLocalPath(self, name, path, bucket=None):
    if os.path.isfile(path):
      print('copying {name} from {path}'.format(name=name, path=path))
      self.set(name, open(path, 'r'), bucket)
    elif os.path.isdir(path):
      print('copying directory  from {path}'.format(name=name, path=path))
      if not bucket:
          bucket = ''
      else:
        bucket += '/'
      bucket += os.path.basename(path)
      # Ensure that empty buckets get created.
      self.createBucket(bucket)
      
      for item in os.listdir(path):
        item_path = os.path.join(path, item)
        self.setFromLocalPath(item, item_path, bucket)

  def get(self, name, bucket=None):
    raise Exception('get method not implemented in ' + self.getClassName())

  def getStream(self, name, bucket=None, mode='r+'):
    raise Exception('getStream method not implemented in ' + self.getClassName())


class FilePipe(object):

  def __init__(self):
    self.files = []

  def setFiles(self, files):
    self.files = files

  def addFile(self, f):
    self.files.append(f)

  def write(self, data):
    for f in self.files:
      f.write(data)

  def close(self):
    for f in self.files:
      f.close()


class OutputPipe(object):

  def __init__(self, outputs=[]):
    self.outputs = outputs

  def prepare(self):
    for output in self.outputs:
      output.prepare()

  def setLogger(self, logger):
    for output in self.outputs:
      output.setLogger(logger)

  def setPrefix(self, prefix):
    for output in self.outputs:
      output.setPrefix(prefix)

  def addOutput(self, output):
    self.outputs.push(output)

  def setOutputs(self, outputs):
    self.outputs = outputs
    
  def createBucket(self, name):
    for output in self.outputs:
      output.createBucket(name)

  def set(self, name, data, bucket=None, mode='w'):
    for output in self.outputs:
      output.set(name, data, bucket, mode)
      
  def setFromLocalPath(self, name, path, bucket=None):
    for output in self.outputs:
      output.setFromLocalPath(name, path, bucket)

  def get(self, name, bucket=None):
    return [output.get(name, bucket) for output in self.outputs]

  def getStream(self, name, bucket=None, mode='r+'):
    pipe = FilePipe()

    for output in self.outputs:
      f = output.getStream(name, bucket, mode)

      if not f:
        raise Exception('Could not open "{bucket}/{file}"" in mode {mode}'.format(
          bucket=bucket,
          file=name,
          mode=mode
        ))

      pipe.addFile(f)

    return pipe
