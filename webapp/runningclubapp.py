#!/usr/bin/python
###########################################################################################
# runningclubapp - web app for running club
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
runningclubapp - web app for running club
=====================================================

URLs supported
* /api/userpw - provide public key and encrypted password support for runningclub database
    * /createuser - create user 
    * /updatekey - update user's private key
    * /updatepw - add or update database password encrypted with user's public key
    * /getpw - retrieve database password encrypted with user's public key
'''
# standard

# google app engine
import webapp2      # also in pypi

# home grown
import userpwapp

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
app = webapp2.WSGIApplication([ ('/api/userpw/createrunningclub', userpwapp.CreateRunningClub),
                                ('/api/userpw/createuser', userpwapp.CreateUser),
                                ('/api/userpw/updateemail', userpwapp.UpdateEmail),
                                ('/api/userpw/updatekey', userpwapp.UpdateKey),
                                ('/api/userpw/updatepw', userpwapp.UpdatePw),
                                ('/api/userpw/getpw', userpwapp.GetPw),
                                ('/api/userpw/getkey', userpwapp.GetKey),
                                #('/.*', MainPage)],
                              ],
                              debug=True)