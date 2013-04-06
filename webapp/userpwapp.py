#!/usr/bin/python
###########################################################################################
# userpwapp - userpw support for running club web app
#
#       Date            Author          Reason
#       ----            ------          ------
#       04/04/13        Lou King        Create
#
#   Copyright 2013 Lou King
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###########################################################################################
'''
userpwapp - userpw support for running club web app
===================================================================

URLs supported
* /api/userpw - provide public key and encrypted password support for runningclub database
    * /createuser - create user 
    * /updateemail - update user's email address
    * /updatekey - update user's private key
    * /updatepw - add or update database password encrypted with user's public key
    * /getpw - retrieve database password encrypted with user's public key
'''

# standard
import webapp2
import datetime
import urllib
import json
import logging

# google app engine
from google.appengine.ext import db

# home grown
import subapp

#----------------------------------------------------------------------
def runningclub_key(runningclub_name):
#----------------------------------------------------------------------
    """Constructs a Datastore key for a RunningClub entry with runningclub_name."""
    keyname = '.userpw.{}'.format(runningclub_name)
    thisrckey = db.Key.from_path('SubApp', '.userpw', 'RunningClub', keyname)
    return thisrckey

#----------------------------------------------------------------------
def getcreateuserpw(runningclub_name,username):
#----------------------------------------------------------------------
    """Returns userpw from database matching username, maybe creates user"""
    pkey = runningclub_key(runningclub_name)
    pname = '.userpw.{}'.format(runningclub_name)
    user = UserPw.get_or_insert('{}.{}'.format(pname,username),parent=pkey)
    return user

#----------------------------------------------------------------------
def getuserpw(runningclub_name,username):
#----------------------------------------------------------------------
    """Returns userpw from database matching username, maybe creates user"""
    pkey = runningclub_key(runningclub_name)
    rcname = '.userpw.{}'.format(runningclub_name)
    uname = '{}.{}'.format(rcname,username)
    key = db.Key.from_path('SubApp', '.userpw', 'RunningClub', rcname, 'UserPw', uname)
    user = UserPw.get(key)
    return user

###########################################################################################
class RunningClub(db.Model):
###########################################################################################
    """Models a RunningClub ."""
    email = db.StringProperty() 

###########################################################################################
class UserPw(db.Model):
###########################################################################################
    """Models an individual Runningclub entry with a username, email, publickey, encrypteddbpassword."""
    username = db.StringProperty()
    email = db.StringProperty() 
    publickey = db.StringProperty(multiline=True)
    encrypteddbpassword = db.TextProperty() # may be longer tha 500 characters
    date = db.DateTimeProperty(auto_now_add=True)

###########################################################################################
class CreateRunningClub(webapp2.RequestHandler):
###########################################################################################
    '''
    create (or update) a runningclub in the database
    '''
    #----------------------------------------------------------------------
    def post(self):
    #----------------------------------------------------------------------
    
        global sakey
        global rckey

        runningclub_name = self.request.get('runningclub')
        email = self.request.get('email')
        
        sa = subapp.SubApp.get_or_insert('.userpw')
        rc = RunningClub.get_or_insert('.userpw.{}'.format(runningclub_name),email=email,parent=sa)
        
        self.response.out.write(json.dumps({'status':'OK'}))


###########################################################################################
class CreateUser(webapp2.RequestHandler):
###########################################################################################
    '''
    create (or update) a user in the database, updating username and email only
    '''
    #----------------------------------------------------------------------
    def post(self):
    #----------------------------------------------------------------------
        runningclub_name = self.request.get('runningclub')
        username = self.request.get('username')
        
        # if user doesn't exist, getcreateuserpw creates it
        user = getcreateuserpw(runningclub_name,username)
        
        user.username = username
        user.put()
        
        self.response.out.write(json.dumps({'status':'OK'}))

###########################################################################################
class UpdateEmail(webapp2.RequestHandler):
###########################################################################################
    '''
    update a userpw in the database, updating email attribute
    '''
    #----------------------------------------------------------------------
    def post(self):
    #----------------------------------------------------------------------
        runningclub_name = self.request.get('runningclub')
        username = self.request.get('username')
        email = self.request.get('email')
        
        user = getuserpw(runningclub_name,username)
        
        # user found, continue
        if user:
            user.email = email
            user.put()
        
            self.response.out.write(json.dumps({'status':'OK'}))
            
        # user not found, error
        else:
            self.response.out.write(json.dumps({'status':'unknownUser'}))

###########################################################################################
class UpdateKey(webapp2.RequestHandler):
###########################################################################################
    '''
    update a userpw in the database, updating publickey attribute
    '''
    #----------------------------------------------------------------------
    def post(self):
    #----------------------------------------------------------------------
        runningclub_name = self.request.get('runningclub')
        username = self.request.get('username')
        publickey = self.request.get('publickey')
        
        user = getuserpw(runningclub_name,username)
        
        # user found, continue
        if user:
            user.publickey = publickey
            user.put()
        
            self.response.out.write(json.dumps({'status':'OK'}))
            
        # user not found, error
        else:
            self.response.out.write(json.dumps({'status':'unknownUser'}))
            
###########################################################################################
class UpdatePw(webapp2.RequestHandler):
###########################################################################################
    '''
    update a userpw in the database, updating encrypteddbpassword attribute
    '''
    #----------------------------------------------------------------------
    def post(self):
    #----------------------------------------------------------------------
        runningclub_name = self.request.get('runningclub')
        username = self.request.get('username')
        encrypteddbpassword = self.request.get('encrypteddbpassword')
        
        user = getuserpw(runningclub_name,username)
        
        # user found, continue
        if user:
            user.encrypteddbpassword = encrypteddbpassword
            user.put()
        
            self.response.out.write(json.dumps({'status':'OK'}))
            
        # user not found, error
        else:
            self.response.out.write(json.dumps({'status':'unknownUser'}))

###########################################################################################
class GetKey(webapp2.RequestHandler):
###########################################################################################
    '''
    retrieve a user's public key
    '''
    #----------------------------------------------------------------------
    def get(self):
    #----------------------------------------------------------------------
        runningclub_name = self.request.get('runningclub')
        username = self.request.get('username')
        
        user = getuserpw(runningclub_name,username)
        
        # user found, continue
        if user:
            publickey = user.publickey
            self.response.out.write(json.dumps({'status':'OK','publickey':publickey}))
            
        # user not found, error
        else:
            self.response.out.write(json.dumps({'status':'unknownUser'}))

###########################################################################################
class GetPw(webapp2.RequestHandler):
###########################################################################################
    '''
    retrieve a users encrypted password
    '''
    #----------------------------------------------------------------------
    def get(self):
    #----------------------------------------------------------------------
        runningclub_name = self.request.get('runningclub')
        username = self.request.get('username')
        
        user = getuserpw(runningclub_name,username)
        
        # user found, continue
        if user:
            encrypteddbpassword = user.encrypteddbpassword
            self.response.out.write(json.dumps({'status':'OK','encrypteddbpassword':encrypteddbpassword}))
            
        # user not found, error
        else:
            self.response.out.write(json.dumps({'status':'unknownUser'}))

