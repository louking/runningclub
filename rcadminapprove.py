###########################################################################################
# rcadminconfig - administrator configuration for running club
#
#	Date		Author		Reason
#	----		------		------
#       04/02/13        Lou King        Create
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
rcadminconfig - administrator configuration for running club
=================================================================

Configure running club information for administrator

Usage::
    TBA
'''

# standard
import pdb
import argparse
import binascii

# pypi
from Crypto.PublicKey import RSA

# github

# other

# home grown
from . import version
from loutilities import extconfigparser
from . import userpw
from .config import CONFIGDIR,PF,SECCF,OPTDBSERVER,OPTDBGLOBUSER,OPTDBPW,OPTUSERPWAPI,OPTCLUBABBREV,parameterError

ADMINCONFIGFILE = 'rcadminconfig.cfg'
ACF = extconfigparser.ConfigFile(CONFIGDIR,ADMINCONFIGFILE)

#----------------------------------------------------------------------
def approve(username): 
#----------------------------------------------------------------------
    '''
    update configuration parameters
    
    :param username: username for user to approve
    '''
    
    # gain access to the web app
    apiurl = getoption(OPTUSERPWAPI)
    persist = userpw.UserPw(apiurl)
    
    # figure out who's password we need, if no global password, then there is one for the user
    dbserver = getoption(OPTDBSERVER)
    pwuser = getoption(OPTDBGLOBUSER)
    if pwuser is None:
        pwuser = username
    
    # find password and encrypt with the user's public key
    password = PF.get(dbserver,pwuser)
    club = getoption(OPTCLUBABBREV)
    userpubkeytext = persist.getpublickey(club,username)
    userpubkey = RSA.importKey(userpubkeytext)
    encryptedpw = userpubkey.encrypt(password,None)[0]
    
    # save encrypted password in the web app
    persist.updateencryptedpw(club,username,encryptedpw)
    
#----------------------------------------------------------------------
def getoption(option): 
#----------------------------------------------------------------------
    '''
    get an option from the configuration file
    
    :param option: name of option
    :rtype: value of option, or None if not found
    '''
    try:
        return ACF.get(SECCF,option)
    except extconfigparser.unknownSection:
        return None
    except extconfigparser.unknownOption:
        return None

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    command line interface for administrative approval of a user
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    
    parser.add_argument('username',help='username to approve')

    args = parser.parse_args()
    username = args.username
    
    approve(username)

###########################################################################################
#	__main__
###########################################################################################
if __name__ == "__main__":
    main()