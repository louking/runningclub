###########################################################################################
# summarizemembers_rsu -- generate member summary
#
#       Date            Author          Reason
#       ----            ------          ------
#       01/05/18        Lou King        Create
#
#   Copyright 2018 Lou King
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

# standard
import argparse
from csv import DictReader
from datetime import datetime, timedelta
from collections import OrderedDict
from json import dumps
import time

# pypi

# homegrown
from running.runsignup import RunSignUp, updatemembercache
from loutilities.csvwt import wlist
from loutilities.configparser import getitems

from loutilities import timeu
ymd = timeu.asctime('%Y-%m-%d')
mdy = timeu.asctime('%m/%d/%Y')
md = timeu.asctime('%m-%d')

import version

class parameterError(Exception): pass

#----------------------------------------------------------------------
def analyzemembership(membercachefile, statsfile=None):
#----------------------------------------------------------------------
    # stats will be unordered dict {year1: {date1:count1, date2:count2...}, year2: {...}, ... }
    stats = {}

    with open(membercachefile, 'rb') as memfile:
        # for each member/membership, add 1 for every date the membership represents
        # only go through today
        today = datetime.now()
        cachedmembers = DictReader(memfile)
        for memberrec in cachedmembers:
            thisdate = ymd.asc2dt( memberrec['JoinDate'] )
            enddate  = ymd.asc2dt( memberrec['ExpirationDate'] )
            while thisdate <= enddate and thisdate <= today:
                thisyear = thisdate.year
                # skip early registrations
                if thisyear >= 2013:     
                    thismd   = md.dt2asc(thisdate)
                    stats.setdefault(thisyear, {})
                    stats[thisyear].setdefault(thismd, 0)
                    stats[thisyear][thismd] += 1
                thisdate += timedelta(1)

    # ordstats = OrderedDict()
    # years = sorted(stats.keys())
    # for year in years:
    #     ordstats[year] = OrderedDict(sorted(stats[year].items(), key=lambda t: t[0]))

    years = stats.keys()
    years.sort()
    statslist = []
    for year in years:
        yearcounts = {'year' : year, 'counts' : [] }
        datecounts = stats[year].keys()
        datecounts.sort()
        for date in datecounts:
            yearcounts['counts'].append( { 'date' : date, 'count' : stats[year][date] } )
        statslist.append( yearcounts )

    if statsfile:
        with open(statsfile, 'wb') as statsf:
            statsjson = dumps(statslist, indent=4, sort_keys=True, separators=(',', ': '))
            statsf.write(statsjson)

    return statslist

#----------------------------------------------------------------------
def summarize(configfile, debug=False):
#----------------------------------------------------------------------
    '''
    Summarize the membership stats and members for a given runsignup club.

    :param configfile: configuration filename
    :param debug: True for requests debugging
    '''

    # configuration file supplied -- pull credentials from the app section
    appconfig = getitems(configfile, 'runsignup')
    club = appconfig['RSU_CLUB']
    membercachefile = appconfig['RSU_CACHEFILE']
    memberstatsfile = appconfig['RSU_STATSFILE']
    key = appconfig['RSU_KEY']
    secret = appconfig['RSU_SECRET']

    # update member cache file
    # note this update is done under lock to prevent any apache thread from disrupting it
    members = updatemembercache(club, membercachefile, key=key, secret=secret, debug=debug)

    # analyze the memberships
    memberstats = analyzemembership(membercachefile, statsfile=memberstatsfile)

    # for debugging
    return members, memberstats


#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    update member cache and summarize member statistics

    configfile must have the following

    [runsignup]

    CLUB: <runsignup club_id>
    KEY: '<key from runsignup partnership'
    SECRET: '<secret from runsignup partnership'
    CACHEFILE: 'input/output csv file which caches individual membership dates'
    STATSFILE: 'output json file which will receive daily member count statistics'
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub', version.__version__))
    parser.add_argument('configfile', help='configuration filename', default=None)
    parser.add_argument('--debug', help='turn on requests debugging', action='store_true')
    args = parser.parse_args()
    
    # summarize membership
    summarize(args.configfile, debug=args.debug)
    
# ##########################################################################################
#   __main__
# ##########################################################################################
if __name__ == "__main__":
    main()
