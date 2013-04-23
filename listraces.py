#!/usr/bin/python
###########################################################################################
# listraces - list race information within database
#
#	Date		Author		Reason
#	----		------		------
#       02/01/13        Lou King        Create
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
listraces - list race information within database
======================================================

'''

# standard
import pdb
import argparse

# pypi

# github

# other

# home grown
import version
import racedb


#----------------------------------------------------------------------
def listraces(session,year=None): 
#----------------------------------------------------------------------
    '''
    list race information for race and raceseries tables
    
    :param session: database session
    :param year: to filter on a specific year
    '''
    
    # TODO: is year necessary if only using active races?
    filters = {'active':True}
    if year:
        filters['year'] = year
        
    # get all the races currently in the database
    # and print the relevant information
    RACELEN = 40
    IDLEN = 6
    cols = '{0:' + str(IDLEN) + 's} {1:10s} {2:' + str(RACELEN) + 's} {3:30s}'
    print cols.format('raceid','date','race','series')
    for race in session.query(racedb.Race).order_by(racedb.Race.year,racedb.Race.racenum).filter_by(**filters):
        theseseries = []
        for rs in session.query(racedb.RaceSeries).filter_by(raceid=race.id,active=True):
            series = session.query(racedb.Series).filter_by(id=rs.seriesid,active=True).first()
            theseseries.append(series.name)
            
        seriesdisplay = ','.join(theseseries)
        print cols.format(str(race.id).rjust(IDLEN),race.date,race.name[0:RACELEN],seriesdisplay)
        
#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    update race information
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('-y','--year',help='year of races to list',default=None, type=int)
    parser.add_argument('-r','--racedb',help='filename of race database (default is as configured during rcuserconfig)',default=None)
    args = parser.parse_args()
    
    racedb.setracedb(args.racedb)
    session = racedb.Session()
    
    listraces(session,args.year)

    session.close()
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
