#!/usr/bin/python
###########################################################################################
# modifyraces - update race information within database
#
#       Date            Author          Reason
#       ----            ------          ------
#       02/01/13        Lou King        Create
#       04/04/13        Lou King        rename from updateraces due to glitch in setuptools/windows8
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
modifyraces - update race information within database
======================================================

Race spreadsheet must have at least the following sheets/columns:

    * races (sheet)
        * race - race name
        * year - year of race
        * date - date of race - may be tentative
        * time - time of race start
        * distance - distance in miles
        * series - comma delimited list of series race is aggregated with

    * series (sheet)
        * series - series name
        * members-only - only aggregated for members (Y|y)
        * overall - aggregated for overall standings (Y|y)
        * divisions - aggregated for division standings (Y|y)
        * age grade - age grade calculated (Y|y)

    * divisions
        * series - name of series division applies to
        * age-low - low age for division (0 for lowest)
        * age-high - high age for division (99 for highest)

'''

# standard
import pdb
import argparse

# pypi

# github

# other

# home grown
from config import dbConsistencyError
import version
import racefile
import racedb

# debug output, maybe
OUT = None

#----------------------------------------------------------------------
def updateraces(session, fileraces): 
#----------------------------------------------------------------------
    '''
    update race information for race table
    
    :param session: database session
    :param fileraces: opened RaceFile object
    '''
    
    # get all the races currently in the database
    # hash them into dict by (name,year)
    allraces = session.query(racedb.Race).filter_by(active=True).all()
    inactiveraces = {}
    for thisrace in allraces:
        inactiveraces[thisrace.name,thisrace.year] = thisrace
        if OUT:
            OUT.write('found id={0}, race={1}\n'.format(thisrace.id,thisrace))
    
    # process each name in race list
    for thisrace in fileraces.getraces():
        # add or update race in database
        race = racedb.Race(thisrace['race'],thisrace['year'],thisrace['racenum'],thisrace['date'],thisrace['time'],thisrace['distance'])
        added = racedb.insert_or_update(session,racedb.Race,race,skipcolumns=['id'],name=race.name,year=race.year)
        
        # remove this race from collection of races which should be deleted in database
        if (race.name,race.year) in inactiveraces:
            inactiveraces.pop((race.name,race.year))
            
        if OUT:
            if added:
                OUT.write('added or updated {0}\n'.format(race))
            else:
                OUT.write('no updates necessary {0}\n'.format(race))
    
    # any races remaining in 'inactiveraces' should be deactivated
    for (name,year) in inactiveraces:
        thisrace = session.query(racedb.Race).filter_by(name=name,year=year).first() # should be only one returned by filter
        thisrace.active = False
        
        if OUT:
            OUT.write('deactivated {0}\n'.format(thisrace))
        
#----------------------------------------------------------------------
def updateseries(session, fileraces): 
#----------------------------------------------------------------------
    '''
    update race information for series table
    
    :param session: database session
    :param fileraces: opened RaceFile object
    '''
    
    # get all the series currently in the database
    # hash them into dict by (name,year)
    allseries = session.query(racedb.Series).filter_by(active=True).all()
    inactiveseries = {}
    for thisseries in allseries:
        inactiveseries[thisseries.name] = thisseries
        if OUT:
            OUT.write('found id={0}, series={1}\n'.format(thisseries.id,thisseries))
    
    # process each name in series list
    allseries = fileraces.getseries()
    for seriesname in allseries:
        # add or update series in database
        thisseries = allseries[seriesname]
        series = racedb.Series(seriesname,thisseries['members-only'],thisseries['overall'],thisseries['divisions'],thisseries['age grade'],
                               thisseries['order by'],thisseries['high to low'],thisseries['average tie'],thisseries['max races'],thisseries['multiplier'],
                               thisseries['max gender'], thisseries['max division'],thisseries['max by runners'])
        added = racedb.insert_or_update(session,racedb.Series,series,skipcolumns=['id'],name=series.name)
        
        # remove this series from collection of series which should be deleted in database
        if series.name in inactiveseries:
            inactiveseries.pop(series.name)
            
        if OUT:
            if added:
                OUT.write('added or updated {0}\n'.format(series))
            else:
                OUT.write('no updates necessary {0}\n'.format(series))
    
    # any series remaining in 'inactiveseries' should be deactivated
    for name in inactiveseries:
        thisseries = session.query(racedb.Series).filter_by(name=name).first() # should be only one returned by filter
        thisseries.active = False
        
        if OUT:
            OUT.write('deactivated {0}\n'.format(thisseries))
        
#----------------------------------------------------------------------
def updateraceseries(session, fileraces): 
#----------------------------------------------------------------------
    '''
    update race information for raceseries table
    note: updateraces and updateseries must be called first
    
    :param session: database session
    :param fileraces: opened RaceFile object
    '''
    
    # get all the raceseries currently in the database
    # hash them into dict by (name,year)
    allraceseries = session.query(racedb.RaceSeries).filter_by(active=True).all()
    inactiveraceseries = {}
    for d in allraceseries:
        inactiveraceseries[(d.raceid,d.seriesid)] = d
        if OUT:
            OUT.write('found raceseries={0}\n'.format(d))
    
    # process each race efinition
    allraces = fileraces.getraces()
    for race in allraces:
        thisrace = session.query(racedb.Race).filter_by(name=race['race'],year=race['year']).first()
        for seriesname in race['inseries']:
            thisseries = session.query(racedb.Series).filter_by(name=seriesname).first()
            
            if not thisseries:
                raise dbConsistencyError,'race refers to series {0}, which was not in database'.format(race['inseries'])
            
            # add or update raceseries in database
            raceseries = racedb.RaceSeries(thisrace.id,thisseries.id)
            added = racedb.insert_or_update(session,racedb.RaceSeries,raceseries,skipcolumns=['id'],raceid=thisrace.id,seriesid=thisseries.id)
        
            # remove this division from collection of divisions which should be deleted in database
            if (thisrace.id,thisseries.id) in inactiveraceseries:
                inactiveraceseries.pop((thisrace.id,thisseries.id))
            
            if OUT:
                if added:
                    OUT.write('added or updated {0}\n'.format(raceseries))
                else:
                    OUT.write('no updates necessary {0}\n'.format(raceseries))
    
    # any divisions remaining in 'inactiveraceseries' should be deactivated
    for d in inactiveraceseries:
        raceid,seriesid = d
        thisraceseries = session.query(racedb.RaceSeries).filter_by(raceid=raceid,seriesid=seriesid).first() # should be only one returned by filter
        thisraceseries.active = False
        
        if OUT:
            OUT.write('deactivated {0}\n'.format(thisraceseries))
        
#----------------------------------------------------------------------
def updatedivisions(session, fileraces): 
#----------------------------------------------------------------------
    '''
    update race information for divisions table
    note: updateseries must be called first
    
    :param session: database session
    :param fileraces: opened RaceFile object
    '''
    
    # get all the divisions currently in the database
    # hash them into dict by (name,year)
    alldivisions = session.query(racedb.Divisions).filter_by(active=True).all()
    inactivedivisions = {}
    for d in alldivisions:
        inactivedivisions[(d.seriesid,d.divisionlow,d.divisionhigh)] = d
        if OUT:
            OUT.write('found division={0}\n'.format(d))
    
    # process each series division definition
    alldivisions = fileraces.getdivisions()
    for seriesname in alldivisions:
        series = session.query(racedb.Series).filter_by(name=seriesname).first()
        if not series:
            raise dbConsistencyError,'division refers to series {0}, which was not in database'.format(thisdivision['series'])
        # add or update division in database
        for divlow,divhigh in alldivisions[seriesname]:
            division = racedb.Divisions(series.id,divlow,divhigh)
            added = racedb.insert_or_update(session,racedb.Divisions,division,skipcolumns=['id'],seriesid=series.id,divisionlow=division.divisionlow,divisionhigh=division.divisionhigh)
        
            # remove this division from collection of divisions which should be deleted in database
            if (series.id,divlow,divhigh) in inactivedivisions:
                inactivedivisions.pop((series.id,divlow,divhigh))
            
            if OUT:
                if added:
                    OUT.write('added or updated {0}\n'.format(division))
                else:
                    OUT.write('no updates necessary {0}\n'.format(division))
    
    # any divisions remaining in 'inactivedivisions' should be deativated
    for d in inactivedivisions:
        seriesid,divlow,divhigh = d
        thisdivision = session.query(racedb.Divisions).filter_by(seriesid=seriesid,divisionlow=divlow,divisionhigh=divhigh).first() # should be only one returned by filter
        thisdivision.active = False
        
        if OUT:
            OUT.write('deativated {0}\n'.format(thisdivision))
        
#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    update race information
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('racefile',help='file with race information')
    parser.add_argument('-r','--racedb',help='filename of race database (default is as configured during rcuserconfig)',default=None)
    parser.add_argument('--debug',help='if set, create updateraces.txt for debugging',action='store_true')
    args = parser.parse_args()
    
    if args.debug:
        global OUT
        OUT = open('updateraces.txt','w')
        
    racedb.setracedb(args.racedb)
    session = racedb.Session()
    
    fileraces = racefile.RaceFile(args.racefile)

    updateraces(session,fileraces)
    updateseries(session,fileraces)
    updateraceseries(session,fileraces)
    updatedivisions(session,fileraces)

    session.commit()
    session.close()

    if OUT:
        OUT.close()
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
