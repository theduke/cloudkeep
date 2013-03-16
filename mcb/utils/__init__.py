from subprocess import *
import tarfile
import sys, os
import pkgutil
import re

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

def parseFormSubmit(session, response, formId):
  """From a requests session and response, parse a form, get its data out and
  send the request.
  """

  soup = BeautifulSoup(r.text)

  data = {}

  form = soup.find('form', id=formId)

  for inp in form.find_all('input', type='hidden'):
    data[inp.attrs['name']] = inp.attrs['value']

  data['email'] = self.username
  data['pass'] = self.password

  url = form.attrs['action']

  response = session.post(url, data)

def loadAllRecusive(package):
  prefix = package.__name__ + "."
  for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
    try:    
      module = __import__(modname, fromlist="*")
    except Exception as e:
      print("Could not load " + modname)
      print(e)
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

def getPlural(noun):
  # (pattern, search, replace) regex english plural rules tuple
  rule_tuple = (
  ('[ml]ouse$', '([ml])ouse$', '\\1ice'), 
  ('child$', 'child$', 'children'), 
  ('booth$', 'booth$', 'booths'), 
  ('foot$', 'foot$', 'feet'), 
  ('ooth$', 'ooth$', 'eeth'), 
  ('l[eo]af$', 'l([eo])af$', 'l\\1aves'), 
  ('sis$', 'sis$', 'ses'), 
  ('man$', 'man$', 'men'), 
  ('ife$', 'ife$', 'ives'), 
  ('eau$', 'eau$', 'eaux'), 
  ('lf$', 'lf$', 'lves'), 
  ('[sxz]$', '$', 'es'), 
  ('[^aeioudgkprt]h$', '$', 'es'), 
  ('(qu|[^aeiou])y$', 'y$', 'ies'), 
  ('$', '$', 's')
  )

  rules = []
  for line in rule_tuple:
    pattern, search, replace = line
    rules.append(lambda word: re.search(pattern, word) and re.sub(search, replace, word))

  for rule in rules:
      result = rule(noun)
      if result: 
          return result

if __name__ == '__main__':
  print(getPlural('service'))
  print(getPlural('output'))
  