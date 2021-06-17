#!/usr/bin/python

import getopt
import sys
import datetime

import httplib2
import json
from oauth2client.file import Storage 
from oauth2client.client import flow_from_clientsecrets
from apiclient.discovery import build
import logging

class OAuth2Installed(object):
    
    flow = flow_from_clientsecrets(filename='client_secret_installed.json',
                             scope='https://www.googleapis.com/auth/userinfo.email',
                             redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    def __init__(self): 
        # logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')                              
        # root = logging.getLogger()
        # root.setLevel(logging.INFO)
            
        # ch = logging.StreamHandler(sys.stdout)
        # ch.setLevel(logging.INFO)
    
        # ch.setFormatter(logFormatter)
        # root.addHandler(ch)
        # logging.getLogger('oauth2client.client').setLevel(logging.DEBUG)
        # logging.getLogger('apiclient.discovery').setLevel(logging.DEBUG)          
         
        storage = Storage('creds.dat')
        credentials = storage.get()

        http = httplib2.Http()  
        if credentials is None or credentials.invalid:             
          auth_uri = self.flow.step1_get_authorize_url()
          print(auth_uri)
          auth_code = input("Enter Auth Code: ")
          credentials = self.flow.step2_exchange(auth_code)
          storage = Storage('creds.dat')
          storage.put(credentials)
        else:
          http = credentials.authorize(http)
          credentials.refresh(http)

        http = credentials.authorize(http)

        print(credentials.access_token)
        print(credentials.id_token)
        
        service = build(serviceName='oauth2', version= 'v2',http=http)          
        resource = service.userinfo()
        slist = resource.get()
        resp = slist.execute() 
        print(json.dumps(resp, sort_keys=True, indent=4))


if __name__ == '__main__':
  OAuth2Installed()
