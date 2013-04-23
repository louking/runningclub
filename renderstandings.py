#!/usr/bin/python
###########################################################################################
# renderstandings - render result information within database for standings
#
#	Date		Author		Reason
#	----		------		------
#       02/14/13        Lou King        Create
#       04/23/13        Lou King        issue #18, render ties correctly
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
renderstandings - render result information within database for standings
==============================================================================

'''

# standard
import pdb
import argparse
import math

# pypi
import xlwt

# github

# other

# home grown
from config import parameterError,dbConsistencyError
import version
import racedb
import render

########################################################################
class BaseStandingsHandler():
########################################################################
    '''
    Base StandingsHandler class -- this is an empty class, to be used as a
    template for filehandler classes.  Each method must be replaced or enhanced.
    
    '''
    #----------------------------------------------------------------------
    def __init__(self,session):
    #----------------------------------------------------------------------
        self.session = session

        self.style = {
            'majorhdr': None,
            'hdr': None,
            'divhdr': None,
            'racehdr': None,
            'racename': None,
            'place': None,
            'name': None,
            'name-won-agegroup': None,
            'name-noteligable': None,
            'race': None,
            'race-dropped': None,
            'total': None,
            }

    #----------------------------------------------------------------------
    def prepare(self,gen,series,year):
    #----------------------------------------------------------------------
        '''
        prepare output file for output, including as appropriate
        
        * open
        * print header information
        * collect format for output
        * collect print line dict for output
        
        numraces has number of races
        
        :param gen: gender M or F
        :param series: racedb.Series
        :param year: year of races
        :rtype: numraces
        '''

        pass
    
    #----------------------------------------------------------------------
    def clearline(self,gen):
    #----------------------------------------------------------------------
        '''
        prepare rendering line for output by clearing all entries

        :param gen: gender M or F
        '''

        pass
    
    #----------------------------------------------------------------------
    def setplace(self,gen,place,stylename='place'):
    #----------------------------------------------------------------------
        '''
        put value in 'place' column for output (this should be rendered in 1st column)

        :param gen: gender M or F
        :param place: value for place column
        :param stylename: name of style for field display
        '''

        pass
    
    #----------------------------------------------------------------------
    def setname(self,gen,name,stylename='name'):
    #----------------------------------------------------------------------
        '''
        put value in 'name' column for output (this should be rendered in 2nd column)

        :param gen: gender M or F
        :param name: value for name column
        :param stylename: name of style for field display
        '''

        pass
    
    #----------------------------------------------------------------------
    def setrace(self,gen,racenum,result,stylename='race'):
    #----------------------------------------------------------------------
        '''
        put value in 'race{n}' column for output, for race n
        should be '' for empty race

        :param gen: gender M or F
        :param racenum: number of race
        :param result: value for race column
        :param stylename: name of style for field display
        '''

        pass
    
    #----------------------------------------------------------------------
    def settotal(self,gen,total,stylename='total'):
    #----------------------------------------------------------------------
        '''
        put value in 'race{n}' column for output, for race n
        should be '' for empty race

        :param gen: gender M or F
        :param value: value for total column
        :param stylename: name of style for field display
        '''

        pass
    
    #----------------------------------------------------------------------
    def render(self,gen):
    #----------------------------------------------------------------------
        '''
        output current line to gender file

        :param gen: gender M or F
        '''

        pass

    #----------------------------------------------------------------------
    def skipline(self,gen):
    #----------------------------------------------------------------------
        '''
        output blank line to gender file

        :param gen: gender M or F
        '''

        pass
    
    #----------------------------------------------------------------------
    def close(self):
    #----------------------------------------------------------------------
        '''
        close files associated with this object
        '''
        
        pass
    
########################################################################
class ListStandingsHandler():
########################################################################
    '''
    Like BaseStandingsHandler class, but adds addhandler method.
    
    file handler operations are done for multiple files
    '''
    #----------------------------------------------------------------------
    def __init__(self):
    #----------------------------------------------------------------------
        self.fhlist = []
    
    #----------------------------------------------------------------------
    def addhandler(self,fh):
    #----------------------------------------------------------------------
        '''
        add derivative of BaseStandingsHandler to list of StandingsHandlers which
        will be processed
        
        :param fh: derivative of BaseStandingsHandler
        '''
        
        self.fhlist.append(fh)
        
    #----------------------------------------------------------------------
    def prepare(self,gen,series,year):
    #----------------------------------------------------------------------
        '''
        prepare output file for output, including as appropriate
        
        * open
        * print header information
        * collect format for output
        * collect print line dict for output
        
        numraces has number of races
        
        :param gen: gender M or F
        :param series: racedb.Series
        :param year: year of races
        :rtype: numraces
        '''
        
        numraces = None
        for fh in self.fhlist:
            numraces = fh.prepare(gen,series,year)
            
        # ok to use the last one
        return numraces
    
    #----------------------------------------------------------------------
    def clearline(self,gen):
    #----------------------------------------------------------------------
        '''
        prepare rendering line for output by clearing all entries

        :param gen: gender M or F
        '''

        for fh in self.fhlist:
            fh.clearline(gen)
    
    #----------------------------------------------------------------------
    def setplace(self,gen,place,stylename='place'):
    #----------------------------------------------------------------------
        '''
        put value in 'place' column for output (this should be rendered in 1st column)

        :param gen: gender M or F
        :param place: value for place column
        :param stylename: name of style for field display
        '''

        for fh in self.fhlist:
            fh.setplace(gen,place,stylename)
    
    #----------------------------------------------------------------------
    def setname(self,gen,name,stylename='name'):
    #----------------------------------------------------------------------
        '''
        put value in 'name' column for output (this should be rendered in 2nd column)

        :param gen: gender M or F
        :param name: value for name column
        :param stylename: name of style for field display
        '''

        for fh in self.fhlist:
            fh.setname(gen,name,stylename)
    
    #----------------------------------------------------------------------
    def setrace(self,gen,racenum,result,stylename='race'):
    #----------------------------------------------------------------------
        '''
        put value in 'race{n}' column for output, for race n
        should be '' for empty race

        :param gen: gender M or F
        :param racenum: number of race
        :param result: value for race column
        :param stylename: name of style for field display
        '''

        for fh in self.fhlist:
            fh.setrace(gen,racenum,result,stylename)
    
    #----------------------------------------------------------------------
    def settotal(self,gen,total,stylename='total'):
    #----------------------------------------------------------------------
        '''
        put value in 'race{n}' column for output, for race n
        should be '' for empty race

        :param gen: gender M or F
        :param value: value for total column
        :param stylename: name of style for field display
        '''

        for fh in self.fhlist:
            fh.settotal(gen,total,stylename)
    
    #----------------------------------------------------------------------
    def render(self,gen):
    #----------------------------------------------------------------------
        '''
        output current line to gender file

        :param gen: gender M or F
        '''

        for fh in self.fhlist:
            fh.render(gen)

    #----------------------------------------------------------------------
    def skipline(self,gen):
    #----------------------------------------------------------------------
        '''
        output blank line to gender file

        :param gen: gender M or F
        '''

        for fh in self.fhlist:
            fh.skipline(gen)
    
    #----------------------------------------------------------------------
    def close(self):
    #----------------------------------------------------------------------
        '''
        close files associated with this object
        '''
        
        for fh in self.fhlist:
            fh.close()
    
########################################################################
class TxtStandingsHandler(BaseStandingsHandler):
########################################################################
    '''
    StandingsHandler for .txt files
    
    :param session: database session
    '''
    #----------------------------------------------------------------------
    def __init__(self,session):
    #----------------------------------------------------------------------
        BaseStandingsHandler.__init__(self,session)
        self.TXT = {}
        self.pline = {'F':{},'M':{}}
    
    #----------------------------------------------------------------------
    def prepare(self,gen,series,year):
    #----------------------------------------------------------------------
        '''
        prepare output file for output, including as appropriate
        
        * open
        * print header information
        * collect format for output
        * collect print line dict for output
        
        numraces has number of races
        
        :param gen: gender M or F
        :param series: racedb.Series
        :param year: year of races
        :rtype: numraces
        '''
        
        # open output file
        MF = {'F':'Women','M':'Men'}
        rengen = MF[gen]
        self.TXT[gen] = open('{0}-{1}-{2}.txt'.format(year,series.name,rengen),'w')
        
        # render list of all races which will be in the series
        self.TXT[gen].write("FSRC {0}'s {1} {2} standings\n".format(rengen,year,series.name))
        self.TXT[gen].write('\n')                
        numraces = 0
        self.racelist = []
        for race in self.session.query(racedb.Race).join("series").filter(racedb.RaceSeries.seriesid==series.id).order_by(racedb.Race.racenum).all():
            self.racelist.append(race.racenum)
            self.TXT[gen].write('\tRace {0}: {1}: {2}\n'.format(race.racenum,race.name,render.renderdate(race.date)))
            numraces += 1
        self.TXT[gen].write('\n')

        # set up cols format string, and render header
        NAMELEN = 40
        COLWIDTH = 5
        self.linefmt = '{{place:5s}} {{name:{0}s}} '.format(NAMELEN)
        for racenum in self.racelist:
            self.linefmt += '{{race{0}:{1}s}} '.format(racenum,COLWIDTH)
        self.linefmt += '{total:10s}\n'
        
        self.clearline(gen)
        self.setplace(gen,'')
        self.setname(gen,'')
        self.settotal(gen,'Total Pts.')
        
        for racenum in self.racelist:
            self.setrace(gen,racenum,racenum)
            
        self.render(gen)

        return numraces
    
    #----------------------------------------------------------------------
    def clearline(self,gen):
    #----------------------------------------------------------------------
        '''
        prepare rendering line for output by clearing all entries

        :param gen: gender M or F
        '''
        
        for k in self.pline[gen]:
            self.pline[gen][k] = ''
    
    #----------------------------------------------------------------------
    def setplace(self,gen,place,stylename='place'):
    #----------------------------------------------------------------------
        '''
        put value in 'place' column for output (this should be rendered in 1st column)

        :param gen: gender M or F
        :param place: value for place column
        :param stylename: name of style for field display
        '''
        
        self.pline[gen]['place'] = str(place)
    
    #----------------------------------------------------------------------
    def setname(self,gen,name,stylename='name'):
    #----------------------------------------------------------------------
        '''
        put value in 'name' column for output (this should be rendered in 2nd column)

        :param gen: gender M or F
        :param name: value for name column
        :param stylename: name of style for field display
        '''
        
        self.pline[gen]['name'] = str(name)
    
    #----------------------------------------------------------------------
    def setrace(self,gen,racenum,result,stylename='race'):
    #----------------------------------------------------------------------
        '''
        put value in 'race{n}' column for output, for race n
        should be '' for empty race

        :param gen: gender M or F
        :param racenum: number of race
        :param result: value for race column
        :param stylename: name of style for field display
        '''
        
        self.pline[gen]['race{0}'.format(racenum)] = str(result)
    
    #----------------------------------------------------------------------
    def settotal(self,gen,total,stylename='total'):
    #----------------------------------------------------------------------
        '''
        put value in 'race{n}' column for output, for race n
        should be '' for empty race

        :param gen: gender M or F
        :param value: value for total column
        :param stylename: name of style for field display
        '''
        
        self.pline[gen]['total'] = str(total)
    
    #----------------------------------------------------------------------
    def render(self,gen):
    #----------------------------------------------------------------------
        '''
        output current line to gender file

        :param gen: gender M or F
        '''

        self.TXT[gen].write(self.linefmt.format(**self.pline[gen]))
    
    #----------------------------------------------------------------------
    def skipline(self,gen):
    #----------------------------------------------------------------------
        '''
        output blank line to gender file

        :param gen: gender M or F
        '''

        self.TXT[gen].write('\n')
    
    #----------------------------------------------------------------------
    def close(self):
    #----------------------------------------------------------------------
        '''
        output blank line to gender file

        :param gen: gender M or F
        '''
        
        for gen in ['F','M']:
            self.TXT[gen].close()
    
########################################################################
class XlStandingsHandler(BaseStandingsHandler):
########################################################################
    '''
    StandingsHandler for .xls files
    
    :param session: database session
    '''
    #----------------------------------------------------------------------
    def __init__(self,session):
    #----------------------------------------------------------------------
        BaseStandingsHandler.__init__(self,session)
        self.wb = xlwt.Workbook()
        self.ws = {}
        
        self.rownum = {'F':0,'M':0}
    
        # height is points*20
        self.style = {
            'majorhdr': xlwt.easyxf('font: bold true, height 240'),
            'hdr': xlwt.easyxf('font: bold true, height 200'),
            'divhdr': xlwt.easyxf('font: bold true, height 200'),
            'racehdr': xlwt.easyxf('align: horiz center; font: bold true, height 200'),
            'racename': xlwt.easyxf('font: height 200'),
            'place': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='general'),
            'name': xlwt.easyxf('font: height 200'),
            'name-won-agegroup': xlwt.easyxf('font: height 200, color green',num_format_str='general'),
            'name-noteligable': xlwt.easyxf('font: height 200, color blue',num_format_str='general'),
            'race': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='general'),
            'race-dropped': xlwt.easyxf('align: horiz center; font: height 200, color red',num_format_str='general'),
            'total': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='general'),
            }
        
    #----------------------------------------------------------------------
    def prepare(self,gen,series,year):
    #----------------------------------------------------------------------
        '''
        prepare output file for output, including as appropriate
        
        * open
        * print header information
        * collect format for output
        * collect print line dict for output
        
        numraces has number of races
        
        :param gen: gender M or F
        :param series: racedb.Series
        :param year: year of races
        :rtype: numraces
        '''
        
        # open output file
        MF = {'F':'Women','M':'Men'}
        rengen = MF[gen]
        self.fname = '{0}-{1}.xls'.format(year,series.name)
        self.ws[gen] = self.wb.add_sheet(rengen)
        
        # render list of all races which will be in the series
        hdrcol = 0
        self.ws[gen].write(self.rownum[gen],hdrcol,"FSRC {0}'s {1} {2} standings\n".format(rengen,year,series.name),self.style['majorhdr'])
        self.rownum[gen] += 1
        hdrcol = 1
        # only drop races if max defined
        if series.maxraces:
            self.ws[gen].write(self.rownum[gen],hdrcol,'Points in red are dropped.',self.style['hdr'])
            self.rownum[gen] += 1
        # don't mention divisions unless series is using divisions
        if series.divisions:
            self.ws[gen].write(self.rownum[gen],hdrcol,'Runners highlighted in blue won an overall award and are not eligible for age group awards.',self.style['hdr'])
            self.rownum[gen] += 1
            self.ws[gen].write(self.rownum[gen],hdrcol,'Runners highlighted in green won an age group award.',self.style['hdr'])
            self.rownum[gen] += 1
        self.rownum[gen] += 1

        self.racelist = []
        self.races = self.session.query(racedb.Race).join("series").filter(racedb.RaceSeries.seriesid==series.id).order_by(racedb.Race.racenum).all()
        numraces = len(self.races)
        nracerows = int(math.ceil(numraces/2.0))
        thiscol = 1
        for racendx in range(nracerows):
            race = self.races[racendx]
            self.racelist.append(race.racenum)
            thisrow = self.rownum[gen]+racendx
            self.ws[gen].write(thisrow,thiscol,'\tRace {0}: {1}: {2}\n'.format(race.racenum,race.name,render.renderdate(race.date)),self.style['racename'])
        thiscol = 6
        for racendx in range(nracerows,numraces):
            race = self.races[racendx]
            self.racelist.append(race.racenum)
            thisrow = self.rownum[gen]+racendx-nracerows
            self.ws[gen].write(thisrow,thiscol,'\tRace {0}: {1}: {2}\n'.format(race.racenum,race.name,render.renderdate(race.date)),self.style['racename'])

        self.rownum[gen] += nracerows+1
        
        # set up column numbers -- reset for each series
        # NOTE: assumes genders are processed within series loop
        self.colnum = {}
        self.colnum['place'] = 0
        self.colnum['name'] = 1
        thiscol = 2
        for racenum in self.racelist:
            self.colnum['race{0}'.format(racenum)] = thiscol
            thiscol += 1
        self.colnum['total'] = thiscol

        # set up col widths
        self.ws[gen].col(self.colnum['place']).width = 6*256
        self.ws[gen].col(self.colnum['name']).width = 19*256
        self.ws[gen].col(self.colnum['total']).width = 9*256
        for racenum in self.racelist:
            self.ws[gen].col(self.colnum['race{0}'.format(racenum)]).width = 6*256
        
        # render header
        self.clearline(gen)
        self.setplace(gen,'')
        self.setname(gen,'')
        self.settotal(gen,'Total Pts.',stylename='racehdr')
        
        for racenum in self.racelist:
            self.setrace(gen,racenum,racenum,stylename='racehdr')
            
        self.render(gen)

        return numraces
    
    #----------------------------------------------------------------------
    def clearline(self,gen):
    #----------------------------------------------------------------------
        '''
        prepare rendering line for output by clearing all entries

        :param gen: gender M or F
        '''
        
        pass    # noop for excel - avoid 'cell overwrite' exception
    
    #----------------------------------------------------------------------
    def setplace(self,gen,place,stylename='place'):
    #----------------------------------------------------------------------
        '''
        put value in 'place' column for output (this should be rendered in 1st column)

        :param gen: gender M or F
        :param place: value for place column
        :param stylename: key into self.style
        '''
        
        self.ws[gen].write(self.rownum[gen],self.colnum['place'],place,self.style[stylename])
    
    #----------------------------------------------------------------------
    def setname(self,gen,name,stylename='name'):
    #----------------------------------------------------------------------
        '''
        put value in 'name' column for output (this should be rendered in 2nd column)

        :param gen: gender M or F
        :param name: value for name column
        :param stylename: key into self.style
        '''
        
        self.ws[gen].write(self.rownum[gen],self.colnum['name'],name,self.style[stylename])
    
    #----------------------------------------------------------------------
    def setrace(self,gen,racenum,result,stylename='race'):
    #----------------------------------------------------------------------
        '''
        put value in 'race{n}' column for output, for race n
        should be '' for empty race

        :param gen: gender M or F
        :param racenum: number of race
        :param result: value for race column
        :param stylename: key into self.style
        '''
        
        # skip races not in this series
        # this is a bit of a kludge but it keeps StandingsRenderer from knowing which races are within each series
        if 'race{0}'.format(racenum) in self.colnum: 
            self.ws[gen].write(self.rownum[gen],self.colnum['race{0}'.format(racenum)],result,self.style[stylename])
    
    #----------------------------------------------------------------------
    def settotal(self,gen,total,stylename='total'):
    #----------------------------------------------------------------------
        '''
        put value in 'race{n}' column for output, for race n
        should be '' for empty race

        :param gen: gender M or F
        :param total: value for total column
        :param stylename: key into self.style
        '''
        
        self.ws[gen].write(self.rownum[gen],self.colnum['total'],total,self.style[stylename])
    
    #----------------------------------------------------------------------
    def render(self,gen):
    #----------------------------------------------------------------------
        '''
        output current line to gender file

        :param gen: gender M or F
        '''

        self.rownum[gen] += 1
    
    #----------------------------------------------------------------------
    def skipline(self,gen):
    #----------------------------------------------------------------------
        '''
        output blank line to gender file

        :param gen: gender M or F
        '''

        self.rownum[gen] += 1
    
    #----------------------------------------------------------------------
    def close(self):
    #----------------------------------------------------------------------
        '''
        output blank line to gender file

        :param gen: gender M or F
        '''
        
        self.wb.save(self.fname)
        
        # kludge to force a new workbook for the next series
        del self.wb
        self.wb = xlwt.Workbook()
        self.rownum = {'F':0,'M':0}
    
########################################################################
class StandingsRenderer():
########################################################################
    '''
    StandingsRenderer collects standings and provides rendering methods, for a single series
    
    :param session: database session
    :param series: racedb.Series
    :param orderby: database field by which standings should be ordered (e.g., racedb.RaceResult.time)
    :param hightolow: True if ordering is high value to low value
    :param bydiv: True if standings are to be tallied by division, in addition to by gender
    :param avgtie: True if tie points are averaged, else max points is used for both
    :param multiplier: race points are multiplied by this value
    :param maxgenpoints: maximum number of points by gender for first place result.  If None, standings are tallied directly
    :param maxdivpoints: maximum number of points by division for first place result
    :param maxraces: maximum number of races run by a runner to be included in total points
    '''
    #----------------------------------------------------------------------
    def __init__(self,session,series,orderby,hightolow,bydiv,avgtie,multiplier=1,maxgenpoints=None,maxdivpoints=None,maxraces=None):
    #----------------------------------------------------------------------
        self.session = session
        self.series = series
        self.orderby = orderby
        self.hightolow = hightolow
        self.bydiv = bydiv
        self.avgtie = avgtie
        self.multiplier = multiplier
        self.maxgenpoints = maxgenpoints
        self.maxdivpoints = maxdivpoints
        self.maxraces = maxraces
        
    #----------------------------------------------------------------------
    def collectstandings(self,racesprocessed,gen,raceid,byrunner,divrunner): 
    #----------------------------------------------------------------------
        '''
        collect standings for this race / series
        
        in byrunner[name][type], points{race} entries are set to '' for race not run, to 0 for race run but no points given
        
        :param racesprocessed: number of races processed so far
        :param gen: gender, M or F
        :param raceid: race.id to collect standings for
        :param byrunner: dict updated as runner standings are collected {name:{'bygender':[points1,points2,...],'bydivision':[points1,points2,...]}}
        :param divrunner: dict updated with runner names by division {div:[runner1,runner2,...],...}
        :rtype: number of standings processed for this race / series
        '''
        numresults = 0
    
        # get all the results currently in the database
        # byrunner = {name:{'bygender':[points,points,...],'bydivision':[points,points,...]}, ...}
        allresults = self.session.query(racedb.RaceResult).order_by(self.orderby).filter_by(raceid=raceid,seriesid=self.series.id,gender=gen).all()
        if self.hightolow: allresults.sort(reverse=True)
        
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
                # if result points depend on the number of runners, update maxgenpoints
                if byrunner:
                    maxgenpoints = len(allresults)
                
                # if starting at the top (i.e., maxgenpoints is non-zero, accumulate points accordingly
                if maxgenpoints:
                    genpoints = self.multiplier*(self.maxgenpoints+1-result.genderplace)
                
                # otherwise, accumulate from the bottom (this should never happen)
                else:
                    genpoints = self.multiplier*result.genderplace
                
                byrunner[name]['bygender'].append(max(genpoints,0))
                if self.bydiv:
                    divpoints = self.multiplier*(self.maxdivpoints+1-result.divisionplace)
                    byrunner[name]['bydivision'].append(max(divpoints,0))
            
            # if result was ordered by agpercent, agpercent is used -- assume no divisions
            elif self.orderby == racedb.RaceResult.agpercent:
                # some combinations don't make sense, and have been commented out
                # TODO: verify combinations in updaterace.py
                
                ## if result points depend on the number of runners, update maxgenpoints
                #if byrunner:
                #    maxgenpoints = len(allresults)
                #
                ## if starting at the top (i.e., maxgenpoints is non-zero, accumulate points accordingly
                #if maxgenpoints:
                #    genpoints = self.multiplier*(self.maxgenpoints+1-result.genderplace)
                #
                ## otherwise, accumulate from the bottom (this should never happen)
                #else:
                genpoints = int(round(self.multiplier*result.agpercent))
                
                byrunner[name]['bygender'].append(max(genpoints,0))
                #if self.bydiv:
                #    divpoints = self.multiplier*(self.maxdivpoints+1-result.divisionplace)
                #    byrunner[name]['bydivision'].append(max(divpoints,0))
            
            elif self.orderby == racedb.RaceResult.agtime:
                # TODO: this section needs to be updated (for decathlon), currently cut/paste from orderby time
                
                # if result points depend on the number of runners, update maxgenpoints
                if byrunner:
                    maxgenpoints = len(allresults)
                
                # if starting at the top (i.e., maxgenpoints is non-zero, accumulate points accordingly
                if maxgenpoints:
                    genpoints = self.multiplier*(self.maxgenpoints+1-result.genderplace)
                
                # otherwise, accumulate from the bottom (this should never happen)
                else:
                    genpoints = self.multiplier*result.genderplace
                
                byrunner[name]['bygender'].append(max(genpoints,0))
                if self.bydiv:
                    divpoints = self.multiplier*(self.maxdivpoints+1-result.divisionplace)
                    byrunner[name]['bydivision'].append(max(divpoints,0))
            
            else:
                raise parameterError, 'results must be ordered by time, agtime or agpercent'
            
        return numresults            
    
    #----------------------------------------------------------------------
    def renderseries(self,fh): 
    #----------------------------------------------------------------------
        '''
        render standings for a single series
        
        see BaseStandingsHandler for methods of fh
        
        :param fh: StandingsHandler object-like
        '''

        # collect divisions, if necessary
        if self.bydiv:
            divisions = []
            for div in self.session.query(racedb.Divisions).filter_by(seriesid=self.series.id,active=True).order_by(racedb.Divisions.divisionlow).all():
                divisions.append((div.divisionlow,div.divisionhigh))
            if len(divisions) == 0:
                raise dbConsistencyError, 'series {0} indicates divisions to be calculated, but no divisions found'.format(self.series.name)

        # Get first race for filename year -- assume all active races are within the same year
        firstrace = self.session.query(racedb.Race).filter_by(active=True).order_by(racedb.Race.racenum).first()
        year = firstrace.year
        
        # process each gender
        for gen in ['F','M']:
            # open file, prepare header, etc
            fh.prepare(gen,self.series,year)
                    
            # collect data for each race, within byrunner dict
            # also track names of runners within each division
            byrunner = {}
            divrunner = None
            if self.bydiv:
                divrunner = {}
                for div in divisions:
                    divrunner[div] = []
                
            racesprocessed = 0
            for race in self.session.query(racedb.Race).join("results").all():
                self.collectstandings(racesprocessed,gen,race.id,byrunner,divrunner)
                racesprocessed += 1
                
            # render standings
            # first by division
            if self.bydiv:
                fh.clearline(gen)
                fh.setplace(gen,'Place','racehdr')
                fh.setname(gen,'Age Group','divhdr')
                fh.render(gen)
                
                for div in divisions:
                    fh.clearline(gen)
                    divlow,divhigh = div
                    if divlow == 0:     divtext = '{0} & Under'.format(divhigh)
                    elif divhigh == 99: divtext = '{0} & Over'.format(divlow)
                    else:               divtext = '{0} to {1}'.format(divlow,divhigh)
                    fh.setname(gen,divtext,'divhdr')
                    fh.render(gen)
                    
                    # calculate runner total points
                    bypoints = []
                    for name in divrunner[div]:
                        # convert each race result to int if possible
                        byrunner[name]['bydivision'] = [int(r) if type(r)==float and r==int(r) else r for r in byrunner[name]['bydivision']]
                        racetotals = byrunner[name]['bydivision'][:]    # make a copy
                        racetotals.sort(reverse=True)
                        # total numbers only, and convert to int if possible
                        racetotals = [r for r in racetotals if type(r) in [int,float]]
                        totpoints = sum(racetotals[:min(self.maxraces,len(racetotals))])
                        # render as integer if result same as integer
                        totpoints = int(totpoints) if totpoints == int(totpoints) else totpoints
                        bypoints.append((totpoints,name))
                    
                    # sort runners within division by total points and render
                    bypoints.sort(reverse=True)
                    thisplace = 1
                    lastpoints = -999
                    for runner in bypoints:
                        totpoints,name = runner
                        fh.clearline(gen)
                        
                        # render place if it's different than last runner's place, else there was a tie
                        renderplace = thisplace
                        if totpoints == lastpoints:
                            renderplace = ''
                        fh.setplace(gen,renderplace)
                        thisplace += 1
                        
                        # render name and total points, remember last total points
                        fh.setname(gen,name)
                        fh.settotal(gen,totpoints)
                        lastpoints = totpoints
                        
                        # render race results
                        racenum = 1
                        for pts in byrunner[name]['bydivision']:
                            fh.setrace(gen,racenum,pts)
                            racenum += 1
                        fh.render(gen)
                        
                    # skip line between divisions
                    fh.skipline(gen)
                        
            # then overall
            fh.clearline(gen)
            fh.setplace(gen,'Place','racehdr')
            fh.setname(gen,'Overall','divhdr')
            fh.render(gen)
            
            # calculate runner total points
            bypoints = []
            for name in byrunner:
                # convert each race result to int if possible
                byrunner[name]['bygender'] = [int(r) if type(r)==float and r==int(r) else r for r in byrunner[name]['bygender']]
                racetotals = byrunner[name]['bygender'][:]    # make a copy
                racetotals.sort(reverse=True)
                # total numbers only, and convert to int if possible
                racetotals = [r for r in racetotals if type(r) in [int,float]]
                totpoints = sum(racetotals[:min(self.maxraces,len(racetotals))])
                totpoints = int(totpoints) if totpoints == int(totpoints) else totpoints
                bypoints.append((totpoints,name))
            
            # sort runners by total points and render
            bypoints.sort(reverse=True)
            thisplace = 1
            lastpoints = -999
            for runner in bypoints:
                totpoints,name = runner
                fh.clearline(gen)
                        
                # render place if it's different than last runner's place, else there was a tie
                renderplace = thisplace
                if totpoints == lastpoints:
                    renderplace = ''
                fh.setplace(gen,renderplace)
                thisplace += 1
                
                # render name and total points, remember last total points
                fh.setname(gen,name)
                fh.settotal(gen,totpoints)
                lastpoints = totpoints
                
                # render race results
                racenum = 1
                for pts in byrunner[name]['bygender']:
                    fh.setrace(gen,racenum,pts)
                    racenum += 1
                fh.render(gen)
            fh.skipline(gen)
                        
        # done with rendering
        fh.close()
            
#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    render result information
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('-s','--series',help='series to render',default=None)
    parser.add_argument('-r','--racedb',help='filename of race database (default is as configured during rcuserconfig)',default=None)
    args = parser.parse_args()
    
    racedb.setracedb(args.racedb)
    session = racedb.Session()
    
    # get filtered series, which have any results
    sfilter = {'active':True}
    theseseries = session.query(racedb.Series).filter_by(**sfilter).join("results").all()
    
    fh = ListStandingsHandler()
    fh.addhandler(TxtStandingsHandler(session))
    fh.addhandler(XlStandingsHandler(session))
    
    for series in theseseries:
        # orderby parameter is specified by the series
        orderby = getattr(racedb.RaceResult,series.orderby)
        
        # render the standings, according to series specifications
        # TODO: now that we are passing series object, can remove many of the parameters
        rr = StandingsRenderer(session,series,orderby,series.hightolow,series.divisions,
                               series.averagetie,multiplier=series.multiplier,maxgenpoints=series.maxgenpoints,
                               maxdivpoints=series.maxdivpoints,maxraces=series.maxraces)
        rr.renderseries(fh)

    session.close()
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
