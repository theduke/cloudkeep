
# Original code was taken from: http://www.tamale.net/imapbackup/imapbackup.py
#
# Original code is under BSD license.
# = Contributors =
# Michael Leonhard
# Bob Ippolito
# Rui Carmo

import os, sys, gc, time, re, hashlib
import imaplib
import mailbox

from mcb.services import Service

class EmailImapService(Service):

  def setup(self):
    self.name = 'email.imap'
    self.pretty_name = 'Email (IMAP)'

    self.addConfig('host', 'Host')
    self.addConfig('port', 'Port', 'int', 143)
    self.addConfig('username', 'Username')
    self.addConfig('password', 'Password')
    self.addConfig('ssl', 'SSL', 'bool', False)
    self.addConfig('compression', 'Compression', 'string', 'none', options={
        'none': 'None',
        'gzip': 'GZIP',
        'bzip2': 'BZIP2'
      }, description="""
Compression to use for the mbox files.
Options: none(default), gzip, bzip2
""")

    self.imap = None
    self.delimiter = None

    self.total_msg_count = 0
    self.finished_msg_count = 0

  def getId(self):
    return self.name + '_' + self.username

  def getPrettyId(self):
    return self.pretty_name + ' - ' + self.username

  def getPluginOutputPrefix(self):
    return self.host + '.' + self.username.replace('@', '_at_')

  # Regular expressions for parsing
  MSGID_RE = re.compile("^Message\-Id\: (.+)", re.IGNORECASE + re.MULTILINE)
  BLANKS_RE = re.compile(r'\s+', re.MULTILINE)

  # Constants
  UUID = '19AF1258-1AAF-44EF-9D9A-731079D6FAD7' # Used to generate Message-Ids

  def downloadMessage(self, msgId, index):
    """Download messages from folder and append to mailbox"""

    # This "From" and the terminating newline below delimit messages
    # in mbox files
    buf = "From nobody {t}\n".format(
      t=time.strftime('%a %m %d %H:%M:%S %Y')
    )

    # If this is one of our synthesised Message-IDs, insert it before
    # the other headers
    if self.UUID in msgId:
      buf = buf + "Message-Id: {id}\n".format(id=msgId)

    # fetch message
    typ, data = self.imap.fetch(index, "RFC822")
    if typ != 'OK':
      raise Exception('FETCH of message {id} with index {index} failed'.format(
        id=msgId,
        index=index
      ))

    text = data[0][1].strip().replace('\r','')
    buf += text
    buf += '\n\n'

    #size = len(text)
    #biggest = max(size, biggest)
    #total += size

    return buf

  def getFileMessageIds(self, filename):
    """Gets IDs of messages in the specified mbox file"""

    try:
      mbox = self.output.getStream(filename, mode='r')
      mbox = mbox.files[0]

      if not mbox:
        # no valid file exists
        return []
    except IOError:
      # file does not exist
      return []

    messages = {}

    # each message
    i = 0
    for message in mailbox.PortableUnixMailbox(mbox):
      header = ''
      # We assume all messages on disk have message-ids
      try:
        header =  ''.join(message.getfirstmatchingheader('message-id'))
      except KeyError:
        # No message ID was found. Warn the user and move on
        self.logger.warn("Message {id} in {file} has no Message-Id header".format(
          id=i,
          file=filename
        ))

      header = self.BLANKS_RE.sub(' ', header.strip())
      try:
        msg_id = self.MSGID_RE.match(header).group(1)
        if msg_id not in messages.keys():
          # avoid adding dupes
          messages[msg_id] = msg_id
      except AttributeError:
        # Message-Id was found but could somehow not be parsed by regexp
        # (highly bloody unlikely)
        self.logger.warn('Message {id} in {file} has a malformed Message-Id header.'.format(
          id=i,
          file=filename
        ))

      i = i + 1

    mbox.close()

    return messages

  def getMessageIdForMailboxMessage(self, index):
    # Retrieve Message-Id
    typ, data = self.imap.fetch(index, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
    if typ != 'OK':
      raise Exception("FETCH of msg {i} failed: {error}".format(
        i=index,
        error=data
      ))

    header = data[0][1].strip()
    # remove newlines inside Message-Id (a dumb Exchange trait)
    header = self.BLANKS_RE.sub(' ', header)
    try:
      msg_id = self.MSGID_RE.match(header).group(1)
    except (IndexError, AttributeError):
      # Some messages may have no Message-Id, so we'll synthesise one
      # (this usually happens with Sent, Drafts and .Mac news)
      typ, data = self.imap.fetch(index, '(BODY[HEADER.FIELDS (FROM TO CC DATE SUBJECT)])')
      if typ != 'OK':
        raise Exception("FETCH of msg {i} failed: {error}".format(
        i=index,
        error=data
      ))

      header = data[0][1].strip()
      header = header.replace('\r\n','\t')

      msg_id = '<' + self.UUID + '.' + hashlib.sha1(header.encode('utf-8')).hexdigest() + '>'

    return msg_id



  def parseParenList(self, row):
    """Parses the nested list of attributes at the start of a LIST response"""
    # eat starting paren
    assert(row[0] == '(')
    row = row[1:]

    result = []

    # NOTE: RFC3501 doesn't fully define the format of name attributes :(
    name_attrib_re = re.compile("^\s*(\\\\[a-zA-Z0-9_]+)\s*")

    # eat name attributes until ending paren
    while row[0] != ')':
      # recurse
      if row[0] == '(':
        paren_list, row = self.parseParenList(row)
        result.append(paren_list)
      # consume name attribute
      else:
        match = name_attrib_re.search(row)
        assert(match != None)
        name_attrib = row[match.start():match.end()]
        row = row[match.end():]

        name_attrib = name_attrib.strip()
        result.append(name_attrib)

    # eat ending paren
    if ')' != row[0]:
      raise Exception('Could not parse paren list')

    row = row[1:]

    # done!
    return result, row

  def parseStringList(self, row):
    """Parses the quoted and unquoted strings at the end of a LIST response"""

    slist = re.compile('\s*(?:"([^"]+)")\s*|\s*(\S+)\s*').split(row)
    return [s for s in slist if s]

  def parseList(self, row):
    """Prases response of LIST command into a list"""

    row = row.strip()
    paren_list, row = self.parseParenList(row)
    string_list = self.parseStringList(row)
    assert(len(string_list) == 2)
    return [paren_list] + string_list

  def getHierarchyDelimiter(self):
    """Queries the imapd for the hierarchy delimiter, eg. '.' in INBOX.Sent"""

    # see RFC 3501 page 39 paragraph 4
    typ, data = self.imap.list('', '')

    if typ != 'OK' or len(data) != 1:
      raise Exception('Could not determine hierarchy delimiter')

    lst = self.parseList(data[0]) # [attribs, hierarchy delimiter, root name]
    hierarchy_delim = lst[1]
    # NIL if there is no hierarchy
    if 'NIL' == hierarchy_delim:
      hierarchy_delim = '.'
    return hierarchy_delim

  def getFolders(self):
    """Get list of folders"""

    # Get LIST of all folders
    typ, data = self.imap.list()
    assert(typ == 'OK')

    folders = []

    # parse each LIST, find folder name
    for row in data:
      lst = self.parseList(row)
      foldername = lst[2]

      folders.append(foldername)

    return folders

  def backupMailbox(self, mbox):
    suffix = {'none':'', 'gzip':'.gz', 'bzip2':'.bz2'}[self.compression]

    filename = '.'.join(mbox.split(self.delimiter))
    filename = filename.replace(' ', '_')
    filename = re.sub(r'[^a-zA-Z0-9\.]', '', filename)
    filename += '.mbox'

    fileMsgIds = self.getFileMessageIds(filename)

    # select mailbox, and get message count
    typ, data = self.imap.select(mbox, readonly=True)
    if typ != 'OK':
      raise Exception("SELECT of folder {mb} failed: {error}".format(
        mb=mbox,
        error=data
      ))
    msgCount = int(data[0])
    self.total_msg_count += msgCount

    stream = self.output.getStream(filename, mode='ab')

    for index in range(1, msgCount+1):
      msgId = self.getMessageIdForMailboxMessage(index)

      self.logger.debug('Processing message with index {index}, id {id}'.format(
        index=index,
        id=msgId
      ))

      if msgId not in fileMsgIds:
        self.logger.debug('Downloading message "{id} with index {index}"'.format(
          id=msgId,
          index=index
        ))
        data = self.downloadMessage(msgId, index)
        stream.write(data)

      self.finished_msg_count += 1
      self.progressHandler.setProgress(self.finished_msg_count / float(self.total_msg_count))

    stream.close()

  def runBackup(self):
    self.logger.debug('Running email backup from {h}:{p}'.format(
      h=self.host,
      p=self.port
    ))

    if self.ssl:
      imap = imaplib.IMAP4_SSL(self.host, self.port)
    else:
      imap = imaplib.IMAP4(self.host, self.port)

    self.logger.debug('Logging in with user {u}'.format(
      u=self.username
    ))

    flag = imap.login(self.username, self.password)
    if not flag:
      self.logger.error('Could not login - wrong credentials?')
      return

    self.logger.debug('Logged in successfully')

    self.imap = imap

     # Get hierarchy delimiter
    self.delimiter = self.getHierarchyDelimiter()

    for mbox in self.getFolders():
      self.logger.info('Processing imap folder "{folder}"'.format(folder=mbox))
      try:
        self.backupMailbox(mbox)
      except Exception as e:
        self.logger.error('Could not process folder {folder}: {error}'.format(
          folder=mbox,
          error=str(e)
        ))

    imap.logout()
