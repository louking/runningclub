#!/usr/bin/python
###########################################################################################
#   config - runningclub configuration constants
#
#   Date        Author      Reason
#   ----        ------      ------
#   01/21/13    Lou King    Create
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
config - runningclub configuration constants
================================================================================
'''

# standard
import os
import os.path
import collections

# pypi
import appdirs

# github

# other

# home grown
from loutilities import extconfigparser

# general purpose exceptions
class accessError(Exception): pass
class parameterError(Exception): pass
class dbConsistencyError(Exception): pass

# configuration location for running scripts
CONFIGDIR = appdirs.user_data_dir('runningclub','Lou King')
if not os.path.exists(CONFIGDIR): os.makedirs(CONFIGDIR)

FILEUSERCONFIG = 'rcuserconfig.cfg'
FILEDBPW = 'rcdbpw.cfg'
FILEUSERKEY = 'rcuser.key'

SECCF = 'runningclub'
SECKEY = 'keys'

# configuration file objects
CF = extconfigparser.ConfigFile(CONFIGDIR,FILEUSERCONFIG)
PF = extconfigparser.ConfigFile(CONFIGDIR,FILEDBPW)
KF = extconfigparser.ConfigFile(CONFIGDIR,FILEUSERKEY)

# options constants for FILEUSERCONFIG and admin config file
OPTCLUBABBREV = 'clubabbrev'
OPTCLUBFULL   = 'clubfull'
OPTEMAIL      = 'email'
OPTUSERPWAPI  = 'userpwpapi'
OPTDBTYPE     = 'dbtype'
OPTDBSERVER   = 'dbserver'
OPTDBNAME     = 'dbname'
OPTDBGLOBUSER = 'dbglobaluser'
OPTUNAME      = 'username'          # not in OPTTBL - for FILEUSERCONFIG only

# options constants for FILEDBPW
OPTDBPW       = 'dbuserpassword'

# options constants for FILEUSERKEY
OPTPRIVKEY    = 'privatekey'
OPTPUBKEY     = 'publickey'

# options table {name:(shorttoption,help),...} for use in config files
# reserved: -u OPTDBGLOBUSER
# TODO: add flags field ADMIN(1)+USER(2)
# TODO: add configuration file object
OPTTBL = collections.OrderedDict([
    (OPTCLUBABBREV ,('-a','abbreviation for club name')),
    (OPTCLUBFULL   ,('-f','full club name')),
    (OPTEMAIL      ,('-e','admin email address')),  # or user email address, special processing in rcuserconfig
    (OPTUSERPWAPI  ,('-w','base url of api to user/password repository')),
    (OPTDBTYPE     ,('-t','type of database, mysql|sqlite')),
    (OPTDBSERVER   ,('-s','server on which club database resides')),
    (OPTDBNAME     ,('-n','database name')),
    (OPTDBGLOBUSER ,('-g','global access username, or None if access requires individual username')),
])
