#!/usr/bin/python

# https://requests-oauthlib.readthedocs.io/en/latest/examples/real_world_example.html

from flask import Flask,redirect, session, request
import logging
import json
import os
import datetime
import urllib, urllib3
from urllib.request import urlopen
from oauth2client.file import Storage 
from google_auth_oauthlib.flow import Flow
import google.oauth2.credentials

from google.auth.transport.requests import AuthorizedSession
from google.auth.credentials import AnonymousCredentials


scopes = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'
redirect_uri='https://localhost.esodemoapp2.com:8081/callback'
client_id='27540059955-redacted.apps.googleusercontent.com'
client_secret='YsujefnJBgv3Gredacted'


app = Flask(__name__)

SESSION_TYPE = "memory"
app.config.update(SECRET_KEY=os.urandom(24))

@app.route("/")
def main():
  if 'username' in session:
      username = session['username']
      return ('Logged in as ' + username + '<br>')
  rdr = ('https://accounts.google.com/o/oauth2/auth?scope=' + urllib.parse.quote(scopes) + '&state=%2Fprofile&redirect_uri=' + urllib.parse.quote(redirect_uri) + '&response_type=code&client_id='+ client_id)
  return redirect(rdr, code=302)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():

    code = request.args.get('code')
    r = ('code [' + code + ']\n')
    url = 'https://accounts.google.com/o/oauth2/token'
    d = {'grant_type' : 'authorization_code',
                'redirect_uri' : redirect_uri,
                'code' : code,
                'client_id' : client_id,
                'client_secret' : client_secret
           }
    headers = {"Content-type": "application/x-www-form-urlencoded"}
         
    data = urllib.parse.urlencode(d).encode("utf-8")
    try:  
      resp = urllib.request.urlopen(url,data).read()
      parsed = json.loads(resp)
      access_token = parsed.get('access_token')
      refresh_token = parsed.get('refresh_token')
      token_uri = parsed.get('token_uri')
      id_token = parsed.get('id_token')
      credentials = google.oauth2.credentials.Credentials(
        access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret)

      authed_session = AuthorizedSession(credentials)
      ar = authed_session.request('GET', 'https://openidconnect.googleapis.com/v1/userinfo')

      session['username'] = ar.json()['email']
    except urllib.error.URLError as e:
      print(e.reason)     
      return (e.reason)      
    except urllib.error.HTTPError as e:
      print(e.reason)
      return (e.reason)     
    return redirect("/", code=302)



if __name__ == '__main__':

  app.run(host='0.0.0.0', port=8081, debug=True, ssl_context=('certs/localhost.crt', 'certs/localhost.key'))