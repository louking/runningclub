#!/usr/bin/python
###########################################################################################
#   updateresults - add results file to race database
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
updateresults - add results file to race database
==========================================================
'''

# standard
import pdb
import argparse
import collections
import os.path
import csv

# pypi
import xlrd

# github

# other

# home grown
from runningclub import *
import version
import racedb
import clubmember
import raceresults
import agegrade
import render
from loutilities import timeu

# module globals
tYmd = timeu.asctime('%Y-%m-%d')
DEBUG = None
ag = agegrade.AgeGrade()

#----------------------------------------------------------------------
def tabulate(session,race,resultsfile,series,active,inactive,INACT,MISSED,CLOSECSV): 
#----------------------------------------------------------------------
    '''
    collect the data, as directed by series attributes
    
    :param session: database session
    :param race: racedb.Race object
    :param resultsfile: file containing results
    :param series: racedb.Series object - describes how to calculate results
    :param active: active members as produced by clubmember.ClubMember()
    :param inactive: inactive members as produced by clubmember.ClubMember()
    :param INACT: filehandle to write inactive member log entries, if desired (else None)
    :param MISSED: filehandle to write log of members which did not match age based on dob in database, if desired (else None)
    :param CLOSECSV: filehandle to write log of members which matched, but not exactly, if desired (else None)
    :rtype: number of entries processed
    '''
    
    # get precision for time rendering
    timeprecision,agtimeprecision = render.getprecision(race.distance)
    
    # get divisions for this series, if appropriate
    if series.divisions:
        alldivs = session.query(racedb.Divisions).filter_by(seriesid=series.id,active=True).all()
        
        if len(alldivs) == 0:
            raise dbConsistencyError, 'series {0} indicates divisions to be calculated, but no divisions found'.format(series.name)
        
        divisions = []
        for div in alldivs:
            divisions.append((div.divisionlow,div.divisionhigh))

        # TODO: remove dead code
        #division = {'F':collections.OrderedDict(),'M':collections.OrderedDict()}
        ## force order of dict.  later delete empty divisions
        #for gender in ['F','M']:
        #    for thisdiv in divisions:
        #        division[gender][thisdiv] = []

    # loop through result entries, collecting overall, bygender and division results
    rr = raceresults.RaceResults(resultsfile,race.distance)
    numentries = 0
    results = []
    while True:
        try:
            result = rr.next()
            results.append(result)
        except StopIteration:
            break
        numentries += 1
    
    # loop through result entries, collecting overall, bygender, division and agegrade results
    for rndx in range(len(results)):
        result = results[rndx]
        
        # some races are for members only
        # for these, don't tabulate unless member found
        foundmember = active.findmember(result['name'],result['age'],race.date)
        foundinactive = inactive.findmember(result['name'],result['age'],race.date)
        
        # log member names found, but which did not match birth date
        if MISSED and not foundmember:
            missed = active.getmissedmatches()
            for thismiss in missed:
                MISSED.write('age mismatch: {0}\n'.format(thismiss))
            
        # log inactive members (members who had previously paid, but are not paid up) who ran this race
        if series.membersonly and not foundmember:
            if foundinactive and INACT:
                name,ascdob = foundinactive
                INACT.write('{0} {1}\n'.format(name,ascdob))
            continue
        
        # for members and inactivemembers, get name, id and genderfrom database (will replace that which was used in results file)
        if foundmember:
            name,ascdob = foundmember
            if CLOSECSV and name != result['name']:
                CLOSECSV.writerow({'results name':result['name'],'results age':result['age'],'database name':name,'database dob':ascdob})
        elif foundinactive:
            name,ascdob = foundinactive
        
        if DEBUG: 
            if foundmember:
                DEBUG.write('{0},{1},{2},{3}\n'.format(result['name'],result['age'],'y',name))
            else:
                DEBUG.write('{0},{1},{2},{3}\n'.format(result['name'],result['age'],'',''))

        if foundmember or foundinactive:
            runner = session.query(racedb.Runner).filter_by(name=name,dateofbirth=ascdob).first()
            runnerid = runner.id
            gender = runner.gender
            dob = tYmd.asc2dt(ascdob)
            
            # set division age (based on age as of Jan 1 for race year)
            # NOTE: the code below assumes that races by divisions are only for members
            # this is because we need to know the runner's age as of Jan 1 for division standings
            racedate = tYmd.asc2dt(race.date)
            divdate = racedate.replace(month=1,day=1)
            divage = divdate.year - dob.year - int((divdate.month, divdate.day) < (dob.month, dob.day))
        
            # for members, set agegrade age (race date based) 
            agegradeage = racedate.year - dob.year - int((racedate.month, racedate.day) < (dob.month, dob.day))
            
        # for non-members, set agegrade age based on results file
        # if non-member, no division awards, because age as of Jan 1 is not known
        # TODO: there may be misspellings in the results file for non-members -- if this occurs, may need to make this more robust
        else:
            name = result['name']
            gender = result['gender']
            divage = None
            
            try:
                agegradeage = int(result['age'])
            except:
                agegradeage = None

        # logic assumes this is always set
        resulttime = result['time']
        if foundmember or foundinactive:
            raceresult = racedb.RaceResult(runnerid,race.id,series.id,resulttime,gender,agegradeage)
        else:
            raceresult = racedb.RaceResult(0,race.id,series.id,resulttime,gender,agegradeage,runnername=name)

        # always add age grade to result if we know the age
        # we will decide whether to render, later based on series.calcagegrade, in another script
        if agegradeage:
            raceresult.agpercent,raceresult.agtime,raceresult.agfactor = ag.agegrade(agegradeage,gender,race.distance,resulttime)

        if series.divisions:
            # member's age to determine division is the member's age on Jan 1
            # if member doesn't give date of birth for membership list, member is not eligible for division awards
            # if non-member, also no division awards, because age as of Jan 1 is not known
            age = divage    # None if not available
            if age:
                # linear search for correct division
                for thisdiv in divisions:
                    divlow = thisdiv[0]
                    divhigh = thisdiv[1]
                    if age in range(divlow,divhigh+1):
                        raceresult.divisionlow = divlow
                        raceresult.divisionhigh = divhigh
                        break

        # make result persistent
        session.add(raceresult)
        
    # process overall and bygender results, sorted by time
    # TODO: is series.overall vs. series.orderby=='time' redundant?  same questio for series.agegrade vs. series.orderby=='agtime'
    if series.orderby == 'time':
        # get all the results which have been stored in the database for this race/series
        ### TODO: use series.orderby, series.hightolow
        dbresults = session.query(racedb.RaceResult).filter_by(raceid=race.id,seriesid=series.id).order_by(racedb.RaceResult.time).all()
        numresults = len(dbresults)
        for rrndx in range(numresults):
            raceresult = dbresults[rrndx]
            
            # set place if it has not been set before
            # place may have been determined at previous iteration, if a tie was detected
            if not raceresult.overallplace:
                thisplace = rrndx+1
                tieindeces = [rrndx]
                
                # detect tie in subsequent results based on rendering,
                # which rounds to a specific precision based on distance
                time = render.rendertime(raceresult.time,timeprecision)
                for tiendx in range(rrndx+1,numresults):
                    if render.rendertime(dbresults[tiendx].time,timeprecision) != time:
                        break
                    tieindeces.append(tiendx)
                lasttie = tieindeces[-1] + 1
                for tiendx in tieindeces:
                    numsametime = len(tieindeces)
                    if numsametime > 1 and series.averagetie:
                        dbresults[tiendx].overallplace = (thisplace+lasttie) / 2.0
                    else:
                        dbresults[tiendx].overallplace = thisplace

        for gender in ['F','M']:
            dbresults = session.query(racedb.RaceResult).filter_by(raceid=race.id,seriesid=series.id,gender=gender).order_by(racedb.RaceResult.time).all()

            numresults = len(dbresults)
            for rrndx in range(numresults):
                raceresult = dbresults[rrndx]
            
                # set place if it has not been set before
                # place may have been determined at previous iteration, if a tie was detected
                if not raceresult.genderplace:
                    thisplace = rrndx+1
                    tieindeces = [rrndx]
                    
                    # detect tie in subsequent results based on rendering,
                    # which rounds to a specific precision based on distance
                    time = render.rendertime(raceresult.time,timeprecision)
                    for tiendx in range(rrndx+1,numresults):
                        if render.rendertime(dbresults[tiendx].time,timeprecision) != time:
                            break
                        tieindeces.append(tiendx)
                    lasttie = tieindeces[-1] + 1
                    for tiendx in tieindeces:
                        numsametime = len(tieindeces)
                        if numsametime > 1 and series.averagetie:
                            dbresults[tiendx].genderplace = (thisplace+lasttie) / 2.0
                        else:
                            dbresults[tiendx].genderplace = thisplace

        if series.divisions:
            for gender in ['F','M']:
                
                # linear search for correct division
                for thisdiv in divisions:
                    divlow = thisdiv[0]
                    divhigh = thisdiv[1]

                    dbresults = session.query(racedb.RaceResult)  \
                                  .filter_by(raceid=race.id,seriesid=series.id,gender=gender,divisionlow=divlow,divisionhigh=divhigh) \
                                  .order_by(racedb.RaceResult.time).all()
        
                    numresults = len(dbresults)
                    for rrndx in range(numresults):
                        raceresult = dbresults[rrndx]

                        # set place if it has not been set before
                        # place may have been determined at previous iteration, if a tie was detected
                        if not raceresult.divisionplace:
                            thisplace = rrndx+1
                            tieindeces = [rrndx]
                            
                            # detect tie in subsequent results based on rendering,
                            # which rounds to a specific precision based on distance
                            time = render.rendertime(raceresult.time,timeprecision)
                            for tiendx in range(rrndx+1,numresults):
                                if render.rendertime(dbresults[tiendx].time,timeprecision) != time:
                                    break
                                tieindeces.append(tiendx)
                            lasttie = tieindeces[-1] + 1
                            for tiendx in tieindeces:
                                numsametime = len(tieindeces)
                                if numsametime > 1 and series.averagetie:
                                    dbresults[tiendx].divisionplace = (thisplace+lasttie) / 2.0
                                else:
                                    dbresults[tiendx].divisionplace = thisplace

    # process age grade results, ordered by agtime
    elif series.orderby == 'agtime':
        for gender in ['F','M']:
            dbresults = session.query(racedb.RaceResult).filter_by(raceid=race.id,seriesid=series.id,gender=gender).order_by(racedb.RaceResult.agtime).all()

            numresults = len(dbresults)
            for rrndx in range(numresults):
                raceresult = dbresults[rrndx]
            
                # set place if it has not been set before
                # place may have been determined at previous iteration, if a tie was detected
                if not raceresult.agtimeplace:
                    thisplace = rrndx+1
                    tieindeces = [rrndx]
                    
                    # detect tie in subsequent results based on rendering,
                    # which rounds to a specific precision based on distance
                    time = render.rendertime(raceresult.agtime,agtimeprecision)
                    for tiendx in range(rrndx+1,numresults):
                        if render.rendertime(dbresults[tiendx].agtime,agtimeprecision) != time:
                            break
                        tieindeces.append(tiendx)
                    lasttie = tieindeces[-1] + 1
                    for tiendx in tieindeces:
                        numsametime = len(tieindeces)
                        if numsametime > 1 and series.averagetie:
                            dbresults[tiendx].agtimeplace = (thisplace+lasttie) / 2.0
                            #if dbresults[tiendx].agtimeplace == (thisplace+lasttie) / 2:
                            #    dbresults[tiendx].agtimeplace = int(dbresults[tiendx].agtimeplace)
                        else:
                            dbresults[tiendx].agtimeplace = thisplace

    # return number of entries processed
    return numentries

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('raceid',help='id of race (use listraces to determine raceid)',type=int)
    parser.add_argument('-f','--resultsfile',help='file with results information',default=None)
    parser.add_argument('-r','--racedbfile',help='filename of race database (default %(default)s)',default='sqlite:///racedb.db')
    parser.add_argument('-d','--delete',help='delete results for this race',action='store_true')
    parser.add_argument('-c','--cutoff',help='cutoff for close match lookup (default %(default)0.2f)',type=float,default=0.7)
    parser.add_argument('--debug',help='if set, create updateraces.txt for debugging',action='store_true')
    args = parser.parse_args()
    
    raceid = args.raceid
    resultsfile = args.resultsfile
    racedbfile = args.racedbfile
    
    if args.debug:
        global DEBUG
        DEBUG = open('updateresults.txt','w')
        DEBUG.write('name in race,age in race,found,member name\n')
    
    # get active and inactive members
    active = clubmember.DbClubMember(racedbfile,cutoff=args.cutoff,active=True)
    inactive = clubmember.DbClubMember(racedbfile,cutoff=args.cutoff,active=False)
    
    # open race database
    racedb.setracedb(racedbfile)
    session = racedb.Session()
    
    # verify race exists
    race = session.query(racedb.Race).filter_by(id=raceid,active=True).first() # should be one of these
    if not race:
        print '*** race id {0} not found in database'.format(raceid)
        return
    
    # make sure the user really wants to do this
    results = session.query(racedb.RaceResult).filter_by(raceid=raceid).all()
    exists = ''
    if results:
        if args.delete:
            exists = '(previously entered race results will be deleted)'
        else:
            exists = '(NOTE: race results already entered, and will be overwritten)'
    elif args.delete:
        print '*** no race results found for {0} {1}'.format(race.year,race.name)
        return
    
    action = 'update'
    if args.delete:
        action = 'delete'
    answer = raw_input('{0} results for {1} {2} {3}? (type yes) '.format(action,race.year,race.name,exists))
    if answer != 'yes':
        print '*** race update aborted -- no changes made'
        return
    
    # first delete all results for this race
    numdeleted = session.query(racedb.RaceResult).filter_by(raceid=raceid).delete()
    if numdeleted:
        print 'deleted {0} entries previously recorded'.format(numdeleted)
        
    
    # only actually update results if --delete option not selected
    if not args.delete:
        
        # TODO: there's probably a cleaner way to do this filter
        raceseries = session.query(racedb.RaceSeries).filter_by(raceid=raceid,active=True).all()
        seriesids = [s.seriesid for s in raceseries]
        theseseries = []
        for seriesid in seriesids:
            theseseries.append(session.query(racedb.Series).filter_by(id=seriesid,active=True).first())
        
        # set up logging files
        logdir = os.path.dirname(resultsfile)
        resultfilebase = os.path.basename(resultsfile)
        inactlogname = 'inactive-{0}.txt'.format(os.path.splitext(resultfilebase)[0])
        INACT = open(os.path.join(logdir,inactlogname),'w')
        missedlogname = 'missed-{0}.txt'.format(os.path.splitext(resultfilebase)[0])
        MISSED = open(os.path.join(logdir,missedlogname),'w')
        closelogname = 'close-{0}.csv'.format(os.path.splitext(resultfilebase)[0])
        CLOSE = open(os.path.join(logdir,closelogname),'wb')
        CLOSECSV = csv.DictWriter(CLOSE,['results name','results age','database name','database dob'])
        CLOSECSV.writeheader()
        
        # for each series - 'series' describes how to tabulate the results
        for series in theseseries:
            # tabulate each race for which there are results, if it hasn't been tabulated before
            print 'tabulating {0}'.format(series.name)
            numentries = tabulate(session,race,resultsfile,series,active,inactive,INACT,MISSED,CLOSECSV)
            print '   {0} entries processed'.format(numentries)
            
            # only collect log entries for the first series
            if INACT:
                INACT.close()
                INACT = None
            if MISSED:
                MISSED.close()
                MISSED = None
            if CLOSECSV:
                CLOSE.close()
                CLOSECSV = None
    
    # and we're through
    session.commit()
    session.close()
    
    # done with memberlookup file
    if DEBUG: DEBUG.close()
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()