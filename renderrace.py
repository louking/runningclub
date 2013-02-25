#!/usr/bin/python
###########################################################################################
# renderrace - render result information within database for specified race
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
renderrace - render result information within database for specified race
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
import render

########################################################################
class BaseRaceHandler():
########################################################################
    '''
    Base RaceHandler class -- this is an empty class, to be used as a
    template for filehandler classes.  Each method must be replaced or enhanced.
    
    :param session: database session
    :param **resultfilter: keyword filter for RaceResult table
    '''
    #----------------------------------------------------------------------
    def __init__(self,session):
    #----------------------------------------------------------------------
        self.session = session
    
    #----------------------------------------------------------------------
    def prepare(self,year,racename):
    #----------------------------------------------------------------------
        '''
        prepare output file for output, including as appropriate
        
        * open
        * print header information
        * collect format for output
        * collect print line dict for output
        
        numraces has number of races
        
        :param year: year of race
        :param racename: name of race
        '''

        pass
    
    #----------------------------------------------------------------------
    def clearline(self):
    #----------------------------------------------------------------------
        '''
        prepare rendering line for output by clearing all entries
        '''

        pass
    
    #----------------------------------------------------------------------
    def setplace(self,place):
    #----------------------------------------------------------------------
        '''
        put value in 'place' column for output (this should be rendered in 1st column)

        :param place: value for place column
        '''

        pass
    
    #----------------------------------------------------------------------
    def setname(self,name):
    #----------------------------------------------------------------------
        '''
        put value in 'name' column for output (this should be rendered in 2nd column)

        :param name: value for name column
        '''

        pass
    
    #----------------------------------------------------------------------
    def setgen(self,gen):
    #----------------------------------------------------------------------
        '''
        put value in 'gen' column for output

        :param gen: gender M or F
        '''

        pass
    
    #----------------------------------------------------------------------
    def setage(self,age):
    #----------------------------------------------------------------------
        '''
        put value in 'age' column for output

        :param age: age on day of race
        '''

        pass
    
    #----------------------------------------------------------------------
    def settime(self,time):
    #----------------------------------------------------------------------
        '''
        put value in 'time' column for output

        :param time: time (seconds)
        '''

        pass
    
    #----------------------------------------------------------------------
    def setagfactor(self,agfactor):
    #----------------------------------------------------------------------
        '''
        put value in 'agpercent' column for output

        :param agfactor: age grade factor (between 0 and 1)
        '''

        pass
    
    #----------------------------------------------------------------------
    def setagpercent(self,agpercent):
    #----------------------------------------------------------------------
        '''
        put value in 'agpercent' column for output

        :param agpercent: age grade percentage (between 0 and 100)
        '''

        pass
    
    #----------------------------------------------------------------------
    def setagtime(self,agtime):
    #----------------------------------------------------------------------
        '''
        put value in 'agtime' column for output

        :param agtime: age grade time (seconds)
        '''

        pass
    
    #----------------------------------------------------------------------
    def render(self):
    #----------------------------------------------------------------------
        '''
        output current line to gender file
        '''

        pass

    #----------------------------------------------------------------------
    def skipline(self):
    #----------------------------------------------------------------------
        '''
        output blank line to gender file
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
class ListRaceHandler():
########################################################################
    '''
    Like BaseRaceHandler class, but adds addhandler method.
    
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
        add derivative of BaseRaceHandler to list of RaceHandlers which
        will be processed
        
        :param fh: derivative of BaseRaceHandler
        '''
        
        self.fhlist.append(fh)
        
    #----------------------------------------------------------------------
    def prepare(self,year,racename):
    #----------------------------------------------------------------------
        '''
        prepare output file for output, including as appropriate
        
        * open
        * print header information
        * collect format for output
        * collect print line dict for output
        
        numraces has number of races
        
        :param year: year of race
        :param racename: name of race
        '''

        for fh in self.fhlist:
            fh.prepare(year,racename)
    
    #----------------------------------------------------------------------
    def clearline(self):
    #----------------------------------------------------------------------
        '''
        prepare rendering line for output by clearing all entries
        '''

        for fh in self.fhlist:
            fh.clearline()
    
    #----------------------------------------------------------------------
    def setplace(self,place):
    #----------------------------------------------------------------------
        '''
        put value in 'place' column for output (this should be rendered in 1st column)

        :param place: value for place column
        '''

        for fh in self.fhlist:
            fh.setplace(place)
    
    #----------------------------------------------------------------------
    def setname(self,name):
    #----------------------------------------------------------------------
        '''
        put value in 'name' column for output (this should be rendered in 2nd column)

        :param name: value for name column
        '''

        for fh in self.fhlist:
            fh.setname(name)
    
    #----------------------------------------------------------------------
    def setage(self,age):
    #----------------------------------------------------------------------
        '''
        put value in 'age' column for output

        :param age: age on day of race
        '''

        for fh in self.fhlist:
            fh.setage(age)
    
    #----------------------------------------------------------------------
    def settime(self,time):
    #----------------------------------------------------------------------
        '''
        put value in 'time' column for output

        :param time: time (seconds)
        '''

        for fh in self.fhlist:
            fh.settime(time)
    
    #----------------------------------------------------------------------
    def setagfactor(self,agfactor):
    #----------------------------------------------------------------------
        '''
        put value in 'agpercent' column for output

        :param agfactor: age grade factor (between 0 and 1)
        '''

        for fh in self.fhlist:
            fh.setagfactor(agfactor)

    #----------------------------------------------------------------------
    def setagpercent(self,agpercent):
    #----------------------------------------------------------------------
        '''
        put value in 'agpercent' column for output

        :param agpercent: age grade percentage (between 0 and 100)
        '''

        for fh in self.fhlist:
            fh.setagpercent(agpercent)
    
    #----------------------------------------------------------------------
    def setagtime(self,agtime):
    #----------------------------------------------------------------------
        '''
        put value in 'agtime' column for output

        :param agtime: age grade time (seconds)
        '''

        for fh in self.fhlist:
            fh.setagtime(agtime)
    
    #----------------------------------------------------------------------
    def render(self):
    #----------------------------------------------------------------------
        '''
        output current line to gender file
        '''

        for fh in self.fhlist:
            fh.render()

    #----------------------------------------------------------------------
    def skipline(self):
    #----------------------------------------------------------------------
        '''
        output blank line to gender file
        '''

        for fh in self.fhlist:
            fh.skipline()
    
    #----------------------------------------------------------------------
    def close(self):
    #----------------------------------------------------------------------
        '''
        close files associated with this object
        '''
        
        for fh in self.fhlist:
            fh.close()
    
########################################################################
class TxtRaceHandler(BaseRaceHandler):
########################################################################
    '''
    RaceHandler for .txt files
    
    :param session: database session
    :param gen: optional gender
    '''
    #----------------------------------------------------------------------
    def __init__(self,session,**resultfilter):
    #----------------------------------------------------------------------

        self.session = session
        self.resultfilter = resultfilter
        
        self.TXT = None
        self.pline = {}
    
    #----------------------------------------------------------------------
    def prepare(self,year,racename):
    #----------------------------------------------------------------------
        '''
        prepare output file for output, including as appropriate
        
        * open
        * print header information
        * collect format for output
        * collect print line dict for output
        
        numraces has number of races
        
        :param year: year of race
        :param racename: name of race
        '''
        
        # open output file
        MF = {'F':'Women','M':'Men'}
        rengen = 'Overall'
        if 'gender' in self.resultfilter:
            rengen = MF[self.resultfilter['gender']]
        self.TXT = open('{0}-{1}-{2}.txt'.format(year,racename,rengen),'w')
        
        # render race
        self.TXT.write("{0} {1} - {2} results\n".format(year,racename,rengen))
        self.TXT.write('\n')                

        # set up cols format string, and render header
        NAMELEN = 40
        COLWIDTH = 5
        self.linefmt = '{{place:5s}} {{name:{0}s}} {{age:3}} {{time:8s}} {{agfactor:7s}} {{agpercent:10s}} {{agtime:8s}}\n'.format(NAMELEN)
        
        self.clearline()
        self.setplace('place')
        self.setname('name')
        self.setage('age')
        self.settime('time')
        self.setagfactor('factor')
        self.setagpercent('age grade')
        self.setagtime('adj time')
        self.render()
    
    #----------------------------------------------------------------------
    def clearline(self):
    #----------------------------------------------------------------------
        '''
        prepare rendering line for output by clearing all entries
        '''
        
        for k in self.pline:
            self.pline[k] = ''
    
    #----------------------------------------------------------------------
    def setplace(self,place):
    #----------------------------------------------------------------------
        '''
        put value in 'place' column for output (this should be rendered in 1st column)

        :param place: value for place column
        '''
        
        self.pline['place'] = str(place)
    
    #----------------------------------------------------------------------
    def setname(self,name):
    #----------------------------------------------------------------------
        '''
        put value in 'name' column for output (this should be rendered in 2nd column)

        :param name: value for name column
        '''
        
        self.pline['name'] = str(name)
    
    #----------------------------------------------------------------------
    def setage(self,age):
    #----------------------------------------------------------------------
        '''
        put value in 'age' column for output

        :param age: age on day of race
        '''
        
        self.pline['age'] = str(age)
    
    #----------------------------------------------------------------------
    def settime(self,time):
    #----------------------------------------------------------------------
        '''
        put value in 'time' column for output

        :param time: time (seconds)
        '''
        
        self.pline['time'] = str(time)
    
    #----------------------------------------------------------------------
    def setagfactor(self,agfactor):
    #----------------------------------------------------------------------
        '''
        put value in 'agpercent' column for output

        :param agfactor: age grade factor (between 0 and 1)
        '''

        self.pline['agfactor'] = str(agfactor)
    
    #----------------------------------------------------------------------
    def setagpercent(self,agpercent):
    #----------------------------------------------------------------------
        '''
        put value in 'agpercent' column for output

        :param agpercent: age grade percentage (between 0 and 100)
        '''
        
        self.pline['agpercent'] = str(agpercent)
    
    #----------------------------------------------------------------------
    def setagtime(self,agtime):
    #----------------------------------------------------------------------
        '''
        put value in 'agtime' column for output

        :param agtime: age grade time (seconds)
        '''
        
        self.pline['agtime'] = str(agtime)
    
    #----------------------------------------------------------------------
    def render(self):
    #----------------------------------------------------------------------
        '''
        output current line to gender file
        '''

        self.TXT.write(self.linefmt.format(**self.pline))
    
    #----------------------------------------------------------------------
    def skipline(self):
    #----------------------------------------------------------------------
        '''
        output blank line to gender file
        '''

        self.TXT.write('\n')
    
    #----------------------------------------------------------------------
    def close(self):
    #----------------------------------------------------------------------
        '''
        close files associated with this object
        '''
        
        self.TXT.close()
    
########################################################################
class RaceRenderer():
########################################################################
    '''
    RaceRenderer collects results and provides rendering methods, for a single series
    
    :param session: database session
    :param racename: race.name
    :param raceid: race.id
    :param orderby: name of field in RaceResult with which results should be ordered (e.g., 'time')
    :param hightolow: True if ordering is high value to low value
    :param **resultfilter: filter parameters for racedb.RaceResult table
    '''
    #----------------------------------------------------------------------
    def __init__(self,session,racename,raceid,orderby,hightolow,**resultfilter):
    #----------------------------------------------------------------------
        self.session = session
        self.racename = racename
        self.raceid = raceid
        self.orderby = orderby
        self.hightolow = hightolow
        self.resultfilter = resultfilter
        
    #----------------------------------------------------------------------
    def renderrace(self,fh): 
    #----------------------------------------------------------------------
        '''
        render results for a single race
        
        fh object has methods with prototypes same as BaseRaceHandler()
        
        :param fh: RaceHandler object-like
        '''

        # Get race information
        race = self.session.query(racedb.Race).filter_by(id=self.raceid).order_by(racedb.Race.racenum).first()
        year = race.year
        timeprecision,agtimeprecision = render.getprecision(race.distance)
        
        # open file, prepare header, etc
        fh.prepare(year,self.racename)
                
        # just use first series found, and get the results associated with this race / series
        series = self.session.query(racedb.Series).join("results").first()
        allresults = self.session.query(racedb.RaceResult).filter_by(raceid=self.raceid,seriesid=series.id,**self.resultfilter).all()
            
        # sort results based on self.orderby field and highlow directive
        dresults = [(getattr(r,self.orderby),r) for r in allresults]
        dresults.sort()
        if self.hightolow: dresults.reverse()
        allresults = [dr[1] for dr in dresults]
        
        # render results
        thisplace = 1
        for result in allresults:
            fh.clearline()
            fh.setplace(thisplace)
            thisplace += 1
            fh.setname(result.runner.name)
            fh.setage(result.agage)
            fh.settime(render.rendertime(result.time,timeprecision))
            fh.setagfactor('{0:0.4f}'.format(result.agfactor))
            fh.setagpercent('{0:0.2f}'.format(result.agpercent))
            fh.setagtime(render.rendertime(result.agtime,agtimeprecision))
            fh.render()
                        
        # done with rendering
        fh.close()
            
#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    render race information
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('raceid',help='id of race (use listraces to determine raceid)',type=int)
    parser.add_argument('-r','--racedb',help='filename of race database (default %(default)s)',default='sqlite:///racedb.db')
    parser.add_argument('-o','--orderby',help='name of RaceResult field to order results by (default %(default)s)',default='time')
    parser.add_argument('-H','--hightolow',help='use if results are to be ordered high value to low value',action='store_true')
    args = parser.parse_args()
    
    raceid = args.raceid
    orderby = args.orderby
    hightolow = args.hightolow
    
    racedb.setracedb(args.racedb)
    session = racedb.Session()
    race = session.query(racedb.Race).filter_by(id=raceid).first()
    if not race:
        print 'raceid {0} not found.  Use listraces to determine raceid'.format(raceid)
        return
    
    # get precision for time, agtime
    
    for gen in [None,'F','M']:
        resultfilter = {}
        if gen:
            resultfilter['gender'] = gen
            
        fh = ListRaceHandler()
        fh.addhandler(TxtRaceHandler(session,**resultfilter))
        
        # render the results, according to specifications
        rr = RaceRenderer(session,race.name,raceid,orderby,hightolow,**resultfilter)
        rr.renderrace(fh)

    session.close()
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
