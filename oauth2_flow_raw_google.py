#!/usr/bin/python

import cherrypy
import httplib
import getopt
import sys
import datetime

import urllib,urllib2
from urllib2 import URLError, HTTPError
import simplejson as json

from oauth2client.client import verify_id_token
from oauth2client.crypt import AppIdentityError
    
class OAuth2(object):

    scopes = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'
    redirect_uri='https://login.yourdomain.com:20000/oauth2callback'
    client_id='187776815091-s310o2fn9arkb8sugq9svf7vifao5ul8.apps.googleusercontent.com'
    client_secret='a0vhgbl21wusklqwK6Nfc1Yf'   

    def index(self):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return "oauth2 test <a href='/profile'>/profile</a>"
    index.exposed = True

    def profile(self):
      rdr = ('https://accounts.google.com/o/oauth2/auth?scope=' + urllib.quote(self.scopes) + '&state=%2Fprofile&redirect_uri=' + urllib.quote(self.redirect_uri) + '&response_type=code&client_id='+ self.client_id)
      raise cherrypy.HTTPRedirect(rdr, 303)
    profile.exposed = True

    def oauth2callback(self,state=None, code=None, *args):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        r = ('code [' + code + ']\n')
        url = 'https://accounts.google.com/o/oauth2/token'
        data = {'grant_type' : 'authorization_code',
                'redirect_uri' : self.redirect_uri,
                'code' : code,
                'client_id' : self.client_id,
                'client_secret' : self.client_secret
                }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
         
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data, headers)
        access_token = None
        id_token = None
        try:
          resp = urllib2.urlopen(req).read()
          parsed = json.loads(resp)
          access_token = parsed.get('access_token')
          r += ('\naccess_token [' + access_token + ']\n')

          id_token = parsed.get('id_token')
          r += ('\n id_token [' + id_token + ']' + ' \n ')

        except HTTPError, e:
          return('Payload: ' + str(e.read()))
        except URLError, e:
          return('Payload: ' + str(e.read))

        try:
          url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=' + access_token
          req = urllib2.Request(url)
          resp = urllib2.urlopen(req).read()
          parsed = json.loads(resp)
          r += ('\nToken Validation: \n' + json.dumps(parsed,sort_keys = False, indent = 4) + '\n')
        except HTTPError, e:
          return('Payload: ' + str(e.read()))
        except URLError, e:
          return('Payload: ' + str(e.read))

        
        try:
          url = 'https://www.googleapis.com/oauth2/v1/userinfo?access_token=' + access_token
          req = urllib2.Request(url)
          resp = urllib2.urlopen(req).read()
          parsed = json.loads(resp)
          id = parsed.get('id')
          r += ('\nUSER PROFILE: \n' + json.dumps(parsed,sort_keys = False, indent = 4) + '\n')
        except HTTPError, e:
          return('Payload: ' + str(e.read()))
        except URLError, e:
          return('Payload: ' + str(e.read))
        

        try:
          jwt = verify_id_token(id_token, self.client_id)     
          r += ('\n ID_TOKEN Validation: \n ' + json.dumps(jwt,sort_keys = False, indent = 4)  +' \n')
        except AppIdentityError, e:
          return('Payload: ' + str(e.read))
          
        return r
    oauth2callback.exposed = True

cherrypy.server.socket_port = 20000
cherrypy.server.socket_host = '0.0.0.0'
cherrypy.config.update({"global": {
          "server.ssl_certificate": "ssl.crt",
          "server.ssl_private_key": "ssl.key",
          'checker.on': False,
          'tools.log_headers.on': True,
          'request.show_tracebacks': False,
          'request.show_mismatched_params': False,
          'log.screen': True}})
cherrypy.quickstart(OAuth2())
