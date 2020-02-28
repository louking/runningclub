#!/usr/bin/python
###########################################################################################
# exportresults - export race results from database
#
#	Date		Author		Reason
#	----		------		------
#       11/20/13        Lou King        Create
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
exportresults - export race results from database
==============================================================================

'''

# standard
import pdb
import argparse
import copy
import csv
import time

# pypi

# github

# other

# home grown
from . import version
from . import racedb
from . import render
from loutilities import timeu
tdb = timeu.asctime('%Y-%m-%d')

METERSPERMILE = 1609.344

#----------------------------------------------------------------------
def collect(outfile,begindate=None,enddate=None,thisracedb=None): 
#----------------------------------------------------------------------
    '''
    collect race information from database, and save to file
    
    :param outfile: output file name template, {date} supported
    :param begindate: collect races between begindate and enddate, yyyy-mm-dd
    :param enddate: collect races between begindate and enddate, yyyy-mm-dd
    :param racedb: filename of race database (default is as configured during rcuserconfig)
    '''
    # TODO: check format of begindate, enddate
    
    # output fields
    outfields = 'name,dob,gender,race,date,miles,km,time,ag'.split(',')
    
    # create/open results file
    tfile = timeu.asctime('%Y-%m-%d')
    fname = outfile.format(date=tfile.epoch2asc(time.time()))
    _OUT = open(fname,'w',newline='')
    OUT = csv.DictWriter(_OUT,outfields)
    OUT.writeheader()
    
    # open the database
    racedb.setracedb(thisracedb)
    session = racedb.Session()

    # for each member, gather results
    members = session.query(racedb.Runner).filter_by(member=True,active=True).all()
    rows = []
    for member in members:
        runnername = member.name
        runnerdob = member.dateofbirth
        runnergender = member.gender

        # loop through each of the runner's results
        # NOTE: results are possibly stored multiple times, for different series -- these will be deduplicated later
        for result in member.results:
            race = session.query(racedb.Race).filter_by(id=result.raceid).first()
            if race.date < begindate or race.date > enddate: continue
            
            resulttime = result.time
            rendertime = render.rendertime(resulttime,0)
            while len(rendertime.split(':')) < 3:
                rendertime = '0:' + rendertime
            resultag = result.agpercent
            racename = race.name
            racedate = race.date
            racemiles = race.distance
            racekm = (race.distance*METERSPERMILE)/1000
            
            # send to output - name,dob,gender,race,date,miles,km,time,ag
            row = {}
            row['name'] = runnername
            row['dob'] = runnerdob
            row['gender'] = runnergender
            row['race'] = racename
            row['date'] = racedate
            row['miles'] = racemiles
            row['km'] = racekm
            row['time'] = rendertime
            row['ag'] = resultag
            if row not in rows:
                rows.append(row)
    
    OUT.writerows(rows)
    
    session.close()
    _OUT.close()

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    render race information
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('-o','--outfile', help="output file name template, default=%(default)s",default='results-export-{date}.csv')
    parser.add_argument('-b','--begindate', help="collect races between begindate and enddate, yyyy-mm-dd",default=None)
    parser.add_argument('-e','--enddate', help="collect races between begindate and enddate, yyyy-mm-dd",default=None)
    parser.add_argument('-r','--racedb',help='filename of race database (default is as configured during rcuserconfig)',default=None)
    args = parser.parse_args()
    
    outfile = args.outfile
    racedb = args.racedb

    if args.begindate:
        begindate = args.begindate
    else:
        begindate = '1970-01-01'
    if args.enddate:
        enddate = args.enddate
    else:
        enddate = '2020-12-31'
    
    collect(outfile,begindate,enddate,racedb)
    
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
