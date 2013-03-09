import dropbox

class DropboxMixin(object):

  def setup(self):
    self.name = 'dropbox'

    self.addConfig('app_key', 'App Key', default='1ykd6aqi5m05m0t')
    self.addConfig('app_secret', 'App Secret', default='qs5ga0gd61fxuz3')

    self.addConfig('username', 'Username')
    self.addConfig('access_token', 'Access Token', default='')
    self.addConfig('access_token_secret', 'Access Token Secret', default='')

    self.session = None
    self.client = None

  def getPluginOutputPrefix(self):
    return self.username

  def getClient(self):
    import dropbox

    self.session = sess = dropbox.session.DropboxSession(
      self.app_key,
      self.app_secret,
      'dropbox'
    )

    if not self.access_token:
      request_token = sess.obtain_request_token()
      url = sess.build_authorize_url(request_token)

      print("url: " + url)
      print("Please visit this website and press the 'Allow' button, then hit 'Enter' here.")
      raw_input()

      access_token = sess.obtain_access_token(request_token)
      self.logger.info('Acquired access token: {token}/{secret}'.format(
        token=access_token.key,
        secret=access_token.secret
      ))

      self.access_token = access_token.key
      self.access_token_secret = access_token.secret
    else:
      sess.set_token(self.access_token, self.access_token_secret)

    client = dropbox.client.DropboxClient(sess)
    return client
