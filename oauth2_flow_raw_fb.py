#!/usr/bin/python

import cherrypy
import httplib
import getopt
import sys
import datetime

import urllib,urllib2
from urllib2 import URLError, HTTPError
import simplejson as json
from urlparse import parse_qs, urlparse
    

    
class OAuth2(object):

    redirect_uri='https://login.yourdomain.com:20000/oauth2callback'
    client_id='488913071285205'
    client_secret='6f1d4509764335b14d901d2ceb586656'    

    def index(self):
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return "oauth2 test <a href='/profile'>/profile</a>"
    index.exposed = True

    def profile(self):  
      rdr = 'https://www.facebook.com/dialog/oauth?client_id=' + self.client_id + '&redirect_uri=' +urllib.quote(self.redirect_uri)
      raise cherrypy.HTTPRedirect(rdr, 303)
    profile.exposed = True

    def oauth2callback(self, code=None, *args):
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        r = ('code [' + code + ']\n')
        print r
        url = 'https://graph.facebook.com/oauth/access_token?'
        data = {
                'redirect_uri' : self.redirect_uri,
                'code' : code,
                'client_id' : self.client_id,
                'client_secret' : self.client_secret
                }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
         
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data, headers)
        access_token = None
        expires = None
        try:
          resp = urllib2.urlopen(req).read()
          qparams = parse_qs(resp)
          access_token =  qparams['access_token'][0] 
          expires =  qparams['expires'][0] 
          r += ('\naccess_token [' + access_token + ']\n expires:' + expires +  '\n')
        except HTTPError, e:
          return('Payload: ' + str(e.read()))
        except URLError, e:
          return('Payload: ' + str(e.read))

        try:
          url = 'https://graph.facebook.com/v2.2/me?fields=id,name&access_token=' + access_token
          req = urllib2.Request(url)
          resp = urllib2.urlopen(req).read()
          r =  r+ '\n' + resp
        except HTTPError, e:
          return('Payload: ' + str(e.read()))
        except URLError, e:
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
