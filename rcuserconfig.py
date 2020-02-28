#!/usr/bin/python
###########################################################################################
# rcuserconfig - user configuration for running club
#
#	Date		Author		Reason
#	----		------		------
#       04/03/13        Lou King        Create
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
rcuserconfig - user configuration for running club
=================================================================

Configure running club information for user

Usage::
    rcuserconfig [-h] [-v] [-k] username email configfile
    
    positional arguments:
      username        user name - get from club administrator
      email           email address
      configfile      name of configuration file - get file from club
                      administrator
    
    optional arguments:
      -h, --help      show this help message and exit
      -v, --version   show program's version number and exit
      -k, --resetkey  use option only to reset encryption keys. It is unusual to
                      need this.

'''

# standard
import pdb
import argparse

# pypi
from Crypto.PublicKey import RSA

# github

# other

# home grown
from . import version
from loutilities import extconfigparser
from .config import CF,KF,OPTTBL,SECCF,OPTUSERPWAPI,OPTCLUBABBREV,OPTUNAME,OPTEMAIL,SECKEY,OPTPRIVKEY,OPTPUBKEY,parameterError
from . import userpw

# will be handle for persistent storage in webapp
PERSIST = None


#----------------------------------------------------------------------
def updateconfig(username,email,configfile,resetkey=False): 
#----------------------------------------------------------------------
    '''
    update configuration parameters
    
    :param configargs: one or more of {args}
    '''.format(args=[OPTUNAME,'configfile','resetkey',])
    
    # process username in logic below which reads configfile
    configargs = {OPTUNAME:username,OPTEMAIL:email}

    # get individual options from configfile
    acp = extconfigparser.ConfigParser()
    acp.read(configfile)
    for opt in acp.options(SECCF):
        configargs[opt] = acp.get(SECCF,opt)

    # process OPTUSERPWAPI first
    if OPTUSERPWAPI in configargs:
        if configargs[OPTUSERPWAPI][-1] != '/':
            configargs[OPTUSERPWAPI] += '/'
        apiurl = configargs[OPTUSERPWAPI] 
        global PERSIST
        PERSIST = userpw.UserPw(apiurl)
    else:
        raise parameterError("'OPTUSERPWAPI' is required")
    
    # options in OPTTBL and OPTUNAME are in the configuration file
    for opt in configargs:
        # normal option
        if opt in OPTTBL or opt==OPTUNAME:
            if configargs[opt] is not None:
                CF.update(SECCF,opt,configargs[opt])
            
        # this should not be able to happen, but...
        else:
            raise parameterError('unknown option {opt}'.format(opt=opt))
            
    # special processing for OPTEMAIL, save email address in webapp
    PERSIST.updateemail(getoption(OPTCLUBABBREV),getoption(OPTUNAME),email)

    # maybe need to update private key
    if resetkey or not getprivkey():
        key = RSA.generate(2048)
        KF.update(SECKEY,OPTPRIVKEY,key.exportKey())
        pubkeyexport = key.publickey().exportKey()
        KF.update(SECKEY,OPTPUBKEY,pubkeyexport)
        # save public key in webapp
        PERSIST.updatekey(getoption(OPTCLUBABBREV),getoption(OPTUNAME),pubkeyexport)
    
#----------------------------------------------------------------------
def getoption(option): 
#----------------------------------------------------------------------
    '''
    get an option from the configuration file
    
    :param option: name of option
    :rtype: value of option, or None if not found
    '''
    try:
        return CF.get(SECCF,option)
    except extconfigparser.unknownSection:
        return None
    except extconfigparser.unknownOption:
        return None

#----------------------------------------------------------------------
def getprivkey(): 
#----------------------------------------------------------------------
    '''
    get private key from the key file
    
    :rtype: value of private key, or None if not found
    '''
    try:
        return KF.get(SECKEY,OPTPRIVKEY)
    except extconfigparser.unknownSection:
        return None
    except extconfigparser.unknownOption:
        return None

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    command line interface to update runningclub configuration
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument(OPTUNAME,help='user name - get from club administrator')
    parser.add_argument(OPTEMAIL,help='email address')
    parser.add_argument('configfile',help='name of configuration file - get file from club administrator')
    parser.add_argument('-k','--resetkey',help='use option only to reset encryption keys.  It is unusual to need this.',action='store_true')
    
    args = parser.parse_args()
    username = vars(args)[OPTUNAME]
    email = vars(args)[OPTEMAIL]
    configfile = args.configfile
    resetkey = args.resetkey
    
    # update user config file with all the options
    updateconfig(username,email,configfile,resetkey)

###########################################################################################
#	__main__
###########################################################################################
if __name__ == "__main__":
    main()