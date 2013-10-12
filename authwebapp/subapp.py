#!/usr/bin/python
###########################################################################################
# subapp - define subsidiary applications for running club
#
#       Date            Author          Reason
#       ----            ------          ------
#       04/05/13        Lou King        Create
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
subapp - define subsidiary applications for running club
=====================================================

'''
# standard

# google app engine
import webapp2      # also in pypi
from google.appengine.ext import db

###########################################################################################
class SubApp(db.Model):
###########################################################################################
    '''
    Models a subsidiary application to runningclub
    
    Each subsidiary application has a module named <subapp>app.py, and is responsible
    for creating the SubApp in the datastore, with SubApp.name=subapp
    
    URLs for each SubApp are of the form /api/<subapp>/<method> for any methods handled by
    the SubApp
    '''
    
    pass
    #name = db.StringProperty()

