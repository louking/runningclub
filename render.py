#!/usr/bin/python
###########################################################################################
# render - common functions for rendering
#
#	Date		Author		Reason
#	----		------		------
#       02/24/13        Lou King        Create
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
render - common functions for rendering
==============================================================================

'''

# standard
import pdb
import argparse

# pypi

# github

# other

# home grown
from runningclub import *
import version
import racedb
DBDATEFMT = racedb.DBDATEFMT
from loutilities import timeu

dbtime = timeu.asctime(DBDATEFMT)
rndrtim = timeu.asctime('%m/%d/%Y')


#----------------------------------------------------------------------
def getprecision(distance): 
#----------------------------------------------------------------------
    '''
    get the precision for rendering, based on distance
    
    precision might be different for time vs. age group adjusted time
    
    :param distance: distance (miles)
    :rtype: (timeprecision,agtimeprecision)
    '''
    
    meterspermile = 1609    # close enough, and this is the value used in agegrade.py
    
    # 200 m plus fudge factor
    if distance*meterspermile < 250:
        timeprecision = 2
        agtimeprecision = 2
        
    # 400 m plus fudge factor
    elif distance*meterspermile < 450:
        timeprecision = 1
        agtimeprecision = 1
        
    # include 1 mile - shouldn't be rounding problem so no fudge factor required
    elif distance <= 1.0:
        timeprecision = 0
        agtimeprecision = 1
        
    # distances > 1 mile
    else:
        timeprecision = 0
        agtimeprecision = 0
        
    return timeprecision, agtimeprecision

#----------------------------------------------------------------------
def renderdate(dbdate): 
#----------------------------------------------------------------------
    '''
    create date for display
    
    :param dbdate: date from database ('yyyy-mm-dd')
    '''
    try:
        dtdate = dbtime.asc2dt(dbdate)
        rval = rndrtim.dt2asc(dtdate)
    except ValueError:
        rval = dbdate
    return rval

#----------------------------------------------------------------------
def rendertime(dbtime,precision): 
#----------------------------------------------------------------------
    '''
    create time for display
    
    :param dbtime: time in seconds
    :param precision: number of places after decimal point
    '''
    
    rettime = ''
    if precision > 0:
        fracdbtime = dbtime - int(dbtime)
        fracformat = '.{{0:0{0}d}}'.format(precision)
        multiplier = 10**precision
        frac = int(round(fracdbtime*multiplier))
        if frac < multiplier:
            rettime = fracformat.format(frac)
            remdbtime = int(dbtime)
        else:
            rettime = fracformat.format(0)
            remdbtime = int(dbtime+1)
    else:
        remdbtime = int(round(dbtime))
    
    thisunit = remdbtime%60
    firstthru = True
    while remdbtime > 0:
        if not firstthru:
            rettime = ':' + rettime
        firstthru = False
        rettime = '{0:02d}'.format(thisunit) + rettime
        remdbtime /= 60
        thisunit = remdbtime%60
        
    while rettime[0] == '0':
        rettime = rettime[1:]
        
    return rettime

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    render unit test
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    #parser.add_argument('raceid',help='id of race (use listraces to determine raceid)',type=int)
    #parser.add_argument('-r','--racedb',help='filename of race database (default %(default)s)',default='sqlite:///racedb.db')
    #parser.add_argument('-o','--orderby',help='name of RaceResult field to order results by (default %(default)s)',default='time')
    #parser.add_argument('-H','--hightolow',help='use if results are to be ordered high value to low value',action='store_true')
    args = parser.parse_args()
    
    # this would be a good place to put unit tests
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
