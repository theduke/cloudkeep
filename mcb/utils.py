from subprocess import *
import tarfile
import sys, os
import pkgutil

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

def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)

    Generator over all subclasses of a given class, in depth first order.

    >>> list(itersubclasses(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>>
    >>> for cls in itersubclasses(A):
    ...     print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """

    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None: _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError: # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub

def loadAllRecusive(package):
  prefix = package.__name__ + "."
  for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
      module = __import__(modname, fromlist="*")
      #print "Imported", module

def getAllServices():
  services = {}

  import mcb.services
  loadAllRecusive(mcb.services)
  for item in itersubclasses(mcb.services.Service):
    name = item().name
    if name:
      services[name] = item

  return services

def getAllOutputs():
  outputs = {}

  import mcb.outputs
  loadAllRecusive(mcb.outputs)
  for item in itersubclasses(mcb.outputs.Output):
    name = item().name
    if name:
      outputs[name] = item

  return outputs

def is_number(s):
  try:
      float(s)
      return True
  except ValueError:
      return False


