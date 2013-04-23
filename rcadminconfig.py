#!/usr/bin/python
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
    rcadminconfig [-h] [-v] [-a CLUBABBREV] [-f CLUBFULL]
                  [-e EMAIL] [-w USERPWPAPI] [-t DBTYPE]
                  [-s DBSERVER] [-n DBNAME] [-g DBGLOBALUSER]
                  [-u DBUSERPASSWORD]
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit
      -a CLUBABBREV, --clubabbrev CLUBABBREV
                            abbreviation for club name. default=FSRC
      -f CLUBFULL, --clubfull CLUBFULL
                            full club name. default=Frederick Steeplechaser
                            Running Club
      -e EMAIL, --email EMAIL
                            admin email address. default=lking@pobox.com
      -w USERPWPAPI, --userpwpapi USERPWPAPI
                            base url of api to user/password repository.
                            default=http://localhost:9080/api/userpw/
      -t DBTYPE, --dbtype DBTYPE
                            type of database, mysql|sqlite. default=mysql
      -s DBSERVER, --dbserver DBSERVER
                            server on which club database resides.
                            default=127.0.0.1
      -n DBNAME, --dbname DBNAME
                            database name. default=racedb
      -g DBGLOBALUSER, --dbglobaluser DBGLOBALUSER
                            global access username, or None if access requires
                            individual username. default=lking
      -u DBUSERPASSWORD, --dbuserpassword DBUSERPASSWORD
                            username[:password] for database. more than one can be
                            specified, separated by commas (no spaces). Use double
                            quotes as some characters in password might get eaten
                            otherwise
                        
'''

# standard
import pdb
import argparse

# pypi

# github

# other

# home grown
import version
from loutilities import extconfigparser
import userpw
from config import CONFIGDIR,PF,OPTTBL,SECCF,OPTDBPW,OPTDBSERVER,OPTUSERPWAPI,OPTCLUBABBREV,OPTEMAIL,parameterError

ADMINCONFIGFILE = 'rcadminconfig.cfg'
ACF = extconfigparser.ConfigFile(CONFIGDIR,ADMINCONFIGFILE)
# will be handle for persistent storage in webapp
PERSIST = None

#----------------------------------------------------------------------
def updateconfig(**configargs): 
#----------------------------------------------------------------------
    '''
    update configuration parameters
    
    :param configargs: one or more of {args}
    '''.format(args=OPTTBL.keys()+[OPTDBPW])
    
    # process OPTUSERPWAPI first
    if OPTUSERPWAPI in configargs:
        if configargs[OPTUSERPWAPI][-1] != '/':
            configargs[OPTUSERPWAPI] += '/'
        apiurl = configargs[OPTUSERPWAPI] 
        global PERSIST
        PERSIST = userpw.UserPw(apiurl)
    else:
        raise parameterError, "'OPTUSERPWAPI' is required"
    
    # options in OPTTBL are in the configuration file
    # other options are in the password file
    users = []
    for opt in configargs:
        # normal option
        if opt in OPTTBL:
            if configargs[opt] is not None:
                
                # special processing for OPTCLUBABBREV
                if opt==OPTCLUBABBREV:
                    # create running club in webapp
                    PERSIST.createrunningclub(configargs[OPTCLUBABBREV],configargs[OPTEMAIL])
                    
                ACF.update(SECCF,opt,configargs[opt])

        # special processing for OPTDBPW
        # password option
        elif opt == OPTDBPW:
            if configargs[OPTDBPW] is not None:
                if configargs[OPTDBSERVER] is None:
                    raise parameterError, "'{server}' option required with '{pw}' option".format(server=OPTDBSERVER,pw=OPTDBPW)
                
                if configargs[OPTCLUBABBREV] is None:
                    raise parameterError, "'{club}' option required with '{pw}' option".format(club=OPTCLUBABBREV,pw=OPTDBPW)
                    
                for unamepw in configargs[OPTDBPW].split(','):
                    unamepwtup = unamepw.split(':')
                    uname = unamepwtup.pop(0)
                    # optional password
                    if len(unamepwtup)>0:
                        pw = unamepwtup.pop(0)
                    else:
                        pw = None
                    
                    # create user in webapp
                    PERSIST.createuser(configargs[OPTCLUBABBREV],uname)
                    
                    # passwords are kept within section by server
                    PF.update(configargs[OPTDBSERVER],uname,pw)
        
        # this should not be able to happen, but...
        else:
            raise parameterError, 'unknown option {opt}'.format(opt=opt)
    
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
    command line interface to update runningclub configuration
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    
    # see config.OPTTBL for option definitions
    cfg = {}
    for opt in OPTTBL.keys():
        cfg[opt] = getoption(opt)
        sopt,helptxt = OPTTBL[opt]
        lopt = '--{opt}'.format(opt=opt)
        parser.add_argument(sopt,lopt,help='{help}.  default=%(default)s'.format(help=helptxt),default=cfg[opt])
    parser.add_argument('-u','--{opt}'.format(opt=OPTDBPW),help='username[:password] for database.  more than one can be specified, separated by commas (no spaces).  Use double quotes as some characters in password might get eaten otherwise')

    args = parser.parse_args()
    updateconfig(**vars(args))

###########################################################################################
#	__main__
###########################################################################################
if __name__ == "__main__":
    main()