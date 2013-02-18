#!/usr/bin/python
###########################################################################################
# renderresults - render result information within database
#
#	Date		Author		Reason
#	----		------		------
#       02/14/13        Lou King        Create
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
renderresults - render result information within database
===========================================================

'''

# standard
import pdb
import argparse

# pypi

# github

# other

# home grown
import version
from running import racedb


#----------------------------------------------------------------------
def rendertime(dbtime): 
#----------------------------------------------------------------------
    '''
    create time for display
    
    :param dbtime: time in seconds
    '''
    
    rettime = ''
    fracdbtime = dbtime - int(dbtime)
    if fracdbtime > 0.0:
        rettime = '.{0:02d}'.format(int(round(fracdbtime*100)))

    remdbtime = int(dbtime)
    
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
    
########################################################################
class ResultsRenderer():
########################################################################
    '''
    ResultsRenderer collects results and provides rendering methods
    
    :param session: database session
    :param orderby: database field by which results should be ordered (e.g., racedb.RaceResult.time)
    :param bydiv: True if results are to be tallied by division, in addition to by gender
    :param avgtie: True if tie points are averaged, else max points is used for both
    :param multiplier: race points are multiplied by this value
    :param maxgenpoints: maximum number of points by gender for first place result.  If None, results are tallied directly
    :param maxdivpoints: maximum number of points by division for first place result
    :param maxraces: maximum number of races run by a runner to be included in total points
    :param resultsfilter: keyword parameters used to retrieve results for a given race
    '''
    #----------------------------------------------------------------------
    def __init__(self,session,orderby,bydiv,avgtie,multiplier=1,maxgenpoints=None,maxdivpoints=None,maxraces=None,**resultsfilter):
    #----------------------------------------------------------------------
        self.session = session
        self.orderby = orderby
        self.bydiv = bydiv
        self.avgtie = avgtie
        self.multiplier = multiplier
        self.maxgenpoints = maxgenpoints
        self.maxdivpoints = maxdivpoints
        self.maxraces = maxraces
        self.resultsfilter = resultsfilter
        
    #----------------------------------------------------------------------
    def collectresults(self,racesprocessed,gen,byrunner,divrunner): 
    #----------------------------------------------------------------------
        '''
        collect results for this race / series
        
        in byrunner[name][type], points{race} entries are set to '' for race not run, to 0 for race run but no points given
        
        :param racesprocessed: number of races processed so far
        :param gen: gender, M or F
        :param byrunner: dict updated as runner results are collected {name:{'bygender':[points1,points2,...],'bydivision':[points1,points2,...]}}
        :param divrunner: dict updated with runner names by division {div:[runner1,runner2,...],...}
        :rtype: number of results processed for this race / series
        '''
        numresults = 0
    
        # get all the results currently in the database
        # byrunner = {name:{'bygender':[points,points,...],'bydivision':[points,points,...]}, ...}
        allresults = self.session.query(racedb.RaceResult).order_by(self.orderby).filter_by(**self.resultsfilter).all()
        for resultndx in range(len(allresults)):
            numresults += 1
            result = allresults[resultndx]
            
            # add runner name 
            name = result.runner.name
            if name not in byrunner:
                byrunner[name] = {}
                byrunner[name]['bygender'] = []
                if self.bydiv:
                    if name not in divrunner[(result.divisionlow,result.divisionhigh)]:
                        divrunner[(result.divisionlow,result.divisionhigh)].append(name)
                    byrunner[name]['bydivision'] = []
            
            # for this runner, catch 'bygender' and 'bydivision' up to current race position
            while len(byrunner[name]['bygender']) < racesprocessed:
                byrunner[name]['bygender'].append('')
                if self.bydiv:
                    byrunner[name]['bydivision'].append('')
                    
            # accumulate points for this result
            # if result is ordered by time, genderplace and divisionplace are used
            if self.orderby == racedb.RaceResult.time:
                genpoints = self.multiplier*(self.maxgenpoints+1-result.genderplace)
                byrunner[name]['bygender'].append(max(genpoints,0))
                if self.bydiv:
                    divpoints = self.multiplier*(self.maxdivpoints+1-result.divisionplace)
                    byrunner[name]['bydivision'].append(max(divpoints,0))
        
        return numresults            
    
#----------------------------------------------------------------------
def collectresults(session,race,racesprocessed,series,gen,byrunner,divrunner): 
#----------------------------------------------------------------------
    '''
    collect results for this race / series
    
    in byrunner[name][type], points{race} entries are set to '' for race not run, to 0 for race run but no points given
    
    :param session: database session
    :param race: racedb.Race row for race being assessed
    :param racesprocessed: number of races processed so far
    :param seriesid: racedb.Series row for series being assessed
    :param gen: gender, M or F
    :param byrunner: dict updated as runner results are collected {name:{'bygender':[points1,points2,...],'bydivision':[points1,points2,...]}}
    :param divrunner: dict updated with runner names by division {div:[runner1,runner2,...],...}
    :rtype: number of results processed for this race / series
    '''
    numresults = 0

    # get all the results currently in the database
    # byrunner = {name:{'bygender':[points,points,...],'bydivision':[points,points,...]}, ...}
    for result in session.query(racedb.RaceResult).order_by(racedb.RaceResult.time).filter_by(raceid=race.id,seriesid=series.id,gender=gen).all():
        numresults += 1
        
        # add runner name 
        name = result.runner.name
        if name not in byrunner:
            byrunner[name] = {}
            byrunner[name]['bygender'] = []
            if series.divisions:
                if name not in divrunner[(result.divisionlow,result.divisionhigh)]:
                    divrunner[(result.divisionlow,result.divisionhigh)].append(name)
                byrunner[name]['bydivision'] = []
        
        # for this runner, catch 'bygender' and 'bydivision' up to current race position
        while len(byrunner[name]['bygender']) < racesprocessed:
            byrunner[name]['bygender'].append('')
            if series.divisions:
                byrunner[name]['bydivision'].append('')
                
        # accumulate points for this result
        ############### refactor ###################
        # TODO: ties require special processing -- this affects updateresults.py as well as here
        if series.name == 'grandprix':
            MAXGEN = 50
            MAXDIV = 10
            byrunner[name]['bygender'].append(max(MAXGEN+1-result.genderplace,0))
            if series.divisions:
                byrunner[name]['bydivision'].append(max(MAXDIV+1-result.divisionplace,0))
    
    return numresults            
    
#----------------------------------------------------------------------
def renderresults(session,seriesfilter): 
#----------------------------------------------------------------------
    '''
    list race information for race and raceseries tables
    
    :param session: database session
    :param seriesfilter: name of series for which results are to be rendered, else None (meaning all series)
    '''
    
    # get filtered series, which have any results
    sfilter = {'active':True}
    if seriesfilter:
        sfilter['name'] = seriesfilter
    theseseries = session.query(racedb.Series).filter_by(**sfilter).join("results").all()
    
    MF = {'F':'Women','M':'Men'}
    TXT = {}
    XLS = {}    # TODO: add xlsx rendering
    
    for thisseries in theseseries:
        # collect divisions, if necessary
        if thisseries.divisions:
            divisions = []
            for div in session.query(racedb.Divisions).filter_by(seriesid=thisseries.id,active=True).order_by(racedb.Divisions.divisionlow).all():
                divisions.append((div.divisionlow,div.divisionhigh))
            if len(divisions) == 0:
                raise dbConsistencyError, 'series {0} indicates divisions to be calculated, but no divisions found'.format(thisseries.name)

        # Get first race for filename year-- assume all races are within the same year
        firstrace = session.query(racedb.Race).join("series").order_by(racedb.Race.racenum).first()
        year = firstrace.year
        
        # process each gender
        for gen in ['F','M']:
            # open output file
            rengen = MF[gen]
            TXT[gen] = open('{0}-{1}-{2}.txt'.format(year,thisseries.name,rengen),'w')
            
            # render list of all races which will be in the series
            numraces = 0
            racenums = []
            TXT[gen].write("FSRC {0}'s {1} {2} standings\n".format(rengen,year,thisseries.name))
            TXT[gen].write('\n')                
            for race in session.query(racedb.Race).join("series").filter(racedb.RaceResult.seriesid==thisseries.id).order_by(racedb.Race.racenum).all():
                TXT[gen].write('\tRace {0}: {1}: {2}\n'.format(race.racenum,race.name,race.date))
                numraces += 1
                racenums.append(race.racenum)
            TXT[gen].write('\n')

            # set up cols format string, and render header
            NAMELEN = 40
            cols = '{place:5s} {name:' + str(NAMELEN) + 's} '
            racenum = 1
            for i in range(numraces):
                cols += '{race' + str(racenum) + ':3s} '
                racenum += 1
            cols += '{total:10s}\n'
            pline = {'place':'','name':'','total':'Total Pts.'}
            for i in range(numraces):
                race = i+1
                pline['race{0}'.format(race)] = str(race)
            TXT[gen].write(cols.format(**pline))

            # collect data for each race, within byrunner dict
            # also track names of runners within each division
            byrunner = {}
            if thisseries.divisions:
                divrunner = {}
                for div in divisions:
                    divrunner[div] = []
                
            racesprocessed = 0
            for race in session.query(racedb.Race).join("results").all():
                collectresults(session,race,racesprocessed,thisseries,gen,byrunner,divrunner)
                racesprocessed += 1
                
            # render results
            # first by division
            if thisseries.divisions:
                for key in pline: pline[key] = ''
                pline['place'] = 'Place'
                pline['name'] = 'Age Group'
                TXT[gen].write(cols.format(**pline))
                
                for div in divisions:
                    for key in pline: pline[key] = ''
                    divlow,divhigh = div
                    if divlow == 0:
                        divtext = '{0} & Under'.format(divhigh)
                    elif divhigh == 99:
                        divtext = '{0} & Over'.format(divlow)
                    else:
                        divtext = '{0} to {1}'.format(divlow,divhigh)
                    pline['name'] = divtext
                    TXT[gen].write(cols.format(**pline))
                    
                    # calculate runner total points
                    bypoints = []
                    for name in divrunner[div]:
                        racetotals = byrunner[name]['bydivision'][:]    # make a copy
                        racetotals.sort(reverse=True)
                        racetotals = [r for r in racetotals if type(r)==int]
                        ############### refactor ###################
                        # TODO: ties require special processing 
                        if thisseries.name == 'grandprix':
                            MAXRACES = 5
                            totpoints = sum(racetotals[:min(MAXRACES,len(racetotals))])
                            bypoints.append((totpoints,name))
                    
                    # sort runners within division by total points and render
                    bypoints.sort(reverse=True)
                    thisplace = 1
                    for runner in bypoints:
                        totpoints,name = runner
                        for key in pline: pline[key] = ''
                        pline['place'] = str(thisplace)
                        thisplace += 1
                        pline['name'] = name
                        pline['total'] = str(totpoints)
                        racenum = 1
                        for pts in byrunner[name]['bydivision']:
                            pline['race{0}'.format(racenum)] = str(pts)
                            racenum += 1
                        TXT[gen].write(cols.format(**pline))
                    TXT[gen].write('\n')
                        
            # then overall
                for key in pline: pline[key] = ''
                pline['place'] = 'Place'
                pline['name'] = 'Overall'
                TXT[gen].write(cols.format(**pline))
                
                # calculate runner total points
                bypoints = []
                for name in byrunner:
                    racetotals = byrunner[name]['bygender'][:]    # make a copy
                    racetotals.sort(reverse=True)
                    racetotals = [r for r in racetotals if type(r)==int]
                    ############### refactor ###################
                    # TODO: ties require special processing 
                    if thisseries.name == 'grandprix':
                        MAXRACES = 5
                        totpoints = sum(racetotals[:min(MAXRACES,len(racetotals))])
                        bypoints.append((totpoints,name))
                
                # sort runners by total points and render
                bypoints.sort(reverse=True)
                thisplace = 1
                for runner in bypoints:
                    totpoints,name = runner
                    for key in pline: pline[key] = ''
                    pline['place'] = str(thisplace)
                    thisplace += 1
                    pline['name'] = name
                    pline['total'] = str(totpoints)
                    racenum = 1
                    for pts in byrunner[name]['bygender']:
                        pline['race{0}'.format(racenum)] = str(pts)
                        racenum += 1
                    TXT[gen].write(cols.format(**pline))
                TXT[gen].write('\n')
                        
            
            # done with rendering
            TXT[gen].close()
            
#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    render result information
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('fsrc',version.__version__))
    parser.add_argument('-r','--racedb',help='filename of race database (default %(default)s)',default='sqlite:///racedb.db')
    parser.add_argument('-s','--series',help='series to render',default=None)
    args = parser.parse_args()
    
    racedb.setracedb(args.racedb)
    session = racedb.Session()
    
    renderresults(session,args.series)

    session.close()
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
