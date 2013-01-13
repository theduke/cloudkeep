# -*- coding: utf-8 -*-


# Code taken from https://github.com/VitaliyRodnenko/geeknote
# Author: Vitaly Rodnenko - vitaliy@rodnenko.ru
# The code does not carry a license, but Vitaly gave personal permission.

import os, sys
import httplib
import time
import Cookie
import uuid
from urllib import urlencode, unquote
from urlparse import urlparse

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class GeekNoteAuth(object):

    consumerKey = None
    consumerSecret = None

    url = {
        "base"  : None,
        "oauth" : "/OAuth.action?oauth_token=%s",
        "access": "/OAuth.action",
        "token" : "/oauth",
        "login" : "/Login.action",
    }

    cookies = {}

    postData = {
        'login': {
            'login': 'Sign in',
            'username': '',
            'password': '',
            'targetUrl': None,
        },
        'access': {
            'authorize': 'Authorize',
            'oauth_token': None,
            'oauth_callback': None,
            'embed': 'false',
        }
    }

    username = None
    password = None
    tmpOAuthToken = None
    verifierToken = None
    OAuthToken = None
    incorrectLogin = 0

    def getTokenRequestData(self, **kwargs):
        params = {
            'oauth_consumer_key': self.consumerKey,
            'oauth_signature': self.consumerSecret+'%26',
            'oauth_signature_method': 'PLAINTEXT',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': uuid.uuid4().hex
        }

        if kwargs:
            params = dict(params.items() + kwargs.items())

        return params

    def loadPage(self, url, uri=None, method="GET", params=""):
        if not url:
            logging.error("Request URL undefined")
            tools.exit()

        if not uri:
            urlData = urlparse(url)
            url = urlData.netloc
            uri = urlData.path + '?' + urlData.query

        # prepare params, append to uri
        if params :
            params = urlencode(params)
            if method == "GET":
                uri += ('?' if uri.find('?') == -1 else '&') + params
                params = ""

        # insert local cookies in request
        headers = {
            "Cookie": '; '.join( [ key+'='+self.cookies[key] for key in self.cookies.keys() ] )
        }

        if method == "POST":
            headers["Content-type"] = "application/x-www-form-urlencoded"

        #logging.debug("Request URL: %s:/%s > %s # %s", url, uri, unquote(params), headers["Cookie"])

        conn = httplib.HTTPSConnection(url)
        conn.request(method, uri, params, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

        #   logging.debug("Response : %s > %s", response.status, response.getheaders())
        result = Struct(status=response.status, location=response.getheader('location', None), data=data)

        # update local cookies
        sk = Cookie.SimpleCookie(response.getheader("Set-Cookie", ""))
        for key in sk:
            self.cookies[key] = sk[key].value

        return result

    def parseResponse(self, data):
        data = unquote(data)
        return dict( item.split('=', 1) for item in data.split('?')[-1].split('&') )


    def getToken(self):
        self.getTmpOAuthToken()

        self.login()

        self.allowAccess()

        self.getOAuthToken()

        #out.preloader.stop()
        return self.OAuthToken


    def getTmpOAuthToken(self):
        response = self.loadPage(self.url['base'], self.url['token'], "GET",
            self.getTokenRequestData(oauth_callback="https://"+self.url['base']))

        if response.status != 200:
            raise Exception('Could not acquire tmp auth token')

        responseData = self.parseResponse(response.data)
        if not responseData.has_key('oauth_token'):
            raise Exception('Could not acquire tmp auth token')

        self.tmpOAuthToken = responseData['oauth_token']

    def login(self):
        response = self.loadPage(self.url['base'], self.url['login'], "GET", {'oauth_token': self.tmpOAuthToken})

        if response.status != 200:
            raise Exception("Unexpected response status on login 200 != {status}"
                .format(status=response.status))

        if not self.cookies.has_key('JSESSIONID'):
            raise Exception("Not found value JSESSIONID in the response cookies")

        # get login/password
        #self.username, self.password = out.GetUserCredentials()

        self.postData['login']['username'] = self.username
        self.postData['login']['password'] = self.password
        self.postData['login']['targetUrl'] = self.url['oauth']%self.tmpOAuthToken
        response = self.loadPage(self.url['base'], self.url['login']+";jsessionid="+self.cookies['JSESSIONID'], "POST",
            self.postData['login'])

        if not response.location and response.status == 200:
            raise Exception('Invalid username/password')

        if not response.location:
            raise Exception("Target URL was not found in the response on login")

        #self.allowAccess(response.location)

    def allowAccess(self):

        self.postData['access']['oauth_token'] = self.tmpOAuthToken
        self.postData['access']['oauth_callback'] = "https://"+self.url['base']
        response = self.loadPage(self.url['base'], self.url['access'], "POST", self.postData['access'])

        if response.status != 302:
            logging.error("Unexpected response status on allowing access 302 != %s", response.status)
            tools.exit()

        responseData = self.parseResponse(response.location)
        if not responseData.has_key('oauth_verifier'):
            logging.error("OAuth verifier not found")
            tools.exit()

        self.verifierToken = responseData['oauth_verifier']

        #logging.debug("OAuth verifier token take")

        #self.getOAuthToken(verifier)

    def getOAuthToken(self):
        response = self.loadPage(self.url['base'], self.url['token'], "GET",
            self.getTokenRequestData(oauth_token=self.tmpOAuthToken, oauth_verifier=self.verifierToken))

        if response.status != 200:
            raise Exception("Unexpected response status on getting oauth token 200 != {r}".format(
                r=response.status))

        responseData = self.parseResponse(response.data)
        if not responseData.has_key('oauth_token'):
            raise Exception("OAuth token not found")

        self.OAuthToken = responseData['oauth_token']
