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
import copy

# pypi
import xlwt

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
    :param distance: race distance (miles)
    :param **resultfilter: keyword filter for RaceResult table
    '''
    #----------------------------------------------------------------------
    def __init__(self,session,distance,**resultfilter):
    #----------------------------------------------------------------------
        self.session = session
    
    #----------------------------------------------------------------------
    def prepare(self,year,racename,orderby):
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
        :param orderby: how results are ordered
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
    def prepare(self,year,racename,orderby):
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
        :param orderby: how results are ordered
        '''

        for fh in self.fhlist:
            fh.prepare(year,racename,orderby)
    
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
    :param distance: race distance (miles)
    :param **resultfilter: keyword filter for RaceResult table
    '''
    #----------------------------------------------------------------------
    def __init__(self,session,distance,**resultfilter):
    #----------------------------------------------------------------------

        self.session = session
        self.resultfilter = resultfilter
        
        self.TXT = None
        self.pline = {}

        self.timeprecision,self.agtimeprecision = render.getprecision(distance)
    
    #----------------------------------------------------------------------
    def prepare(self,year,racename,orderby):
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
        :param orderby: how results are ordered
        '''
        
        # open output file
        MF = {'F':'Women','M':'Men'}
        rengen = 'Overall'
        if 'gender' in self.resultfilter:
            rengen = MF[self.resultfilter['gender']]
        self.TXT = open('{0}-{1}-{2}-{3}.txt'.format(year,racename,rengen,orderby),'w')
        
        # render race
        self.TXT.write("{0} {1} - {2} results, ordered by {3}\n".format(year,racename,rengen,orderby))
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
        
        if type(time) in [str,unicode]:
            dtime = time
        else:
            dtime = render.rendertime(time,self.timeprecision)
        self.pline['time'] = dtime
    
    #----------------------------------------------------------------------
    def setagfactor(self,agfactor):
    #----------------------------------------------------------------------
        '''
        put value in 'agfactor' column for output

        :param agfactor: age grade factor (between 0 and 1)
        '''

        if type(agfactor) == float:
            self.pline['agfactor'] = '{0:0.4f}'.format(agfactor)
        else:
            self.pline['agfactor'] = agfactor
    
    #----------------------------------------------------------------------
    def setagpercent(self,agpercent):
    #----------------------------------------------------------------------
        '''
        put value in 'agpercent' column for output

        :param agpercent: age grade percentage (between 0 and 100)
        '''
        
        if type(agpercent) == float:
            self.pline['agpercent'] = '{0:0.2f}'.format(agpercent)
        else:
            self.pline['agpercent'] = agpercent
    
    #----------------------------------------------------------------------
    def setagtime(self,agtime):
    #----------------------------------------------------------------------
        '''
        put value in 'agtime' column for output

        :param agtime: age grade time (seconds)
        '''
        
        if type(agtime) in [str,unicode]:
            dtime = agtime
        else:
            dtime = render.rendertime(agtime,self.agtimeprecision)
        self.pline['agtime'] = dtime
    
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
class XlRaceHandler(BaseRaceHandler):
########################################################################
    '''
    RaceHandler for .xls files
    
    :param session: database session
    :param distance: race distance (miles)
    :param **resultfilter: keyword filter for RaceResult table
    '''
    #----------------------------------------------------------------------
    def __init__(self,session,distance,**resultfilter):
    #----------------------------------------------------------------------

        self.session = session
        self.resultfilter = resultfilter
        
        self.wb = xlwt.Workbook()

        # height is points*20
        self.style = {
            'majorhdr': xlwt.easyxf('font: bold true, height 240'),
            'hdr': xlwt.easyxf('font: bold true, height 200'),
            'bold': xlwt.easyxf('font: bold true'),
            'ctrhdr': xlwt.easyxf('font: bold true, height 200'),
            'place': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='general'),
            'name': xlwt.easyxf('font: height 200'),
            'age': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='general'),
            'time0': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='h:mm:ss;@'),
            'stime0': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='mm:ss;@'),
            'time1': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='mm:ss.0;@'),
            'time2': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='mm:ss.00;@'),
            'agfactor': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='0.0000'),
            'agpercent': xlwt.easyxf('align: horiz center; font: height 200',num_format_str='0.00'),
            }
    
        # set time styles based on distance
        timeprecision,agtimeprecision = render.getprecision(distance)

        if   timeprecision == 1:   self.style['time'] = self.style['time1']
        elif timeprecision == 2:   self.style['time'] = self.style['time2']
        elif distance <= 3.2:      self.style['time'] = self.style['stime0']
        else:                      self.style['time'] = self.style['time0']

        if   agtimeprecision == 1: self.style['agtime'] = self.style['time1']
        elif agtimeprecision == 2: self.style['agtime'] = self.style['time2']
        elif distance <= 3.2:      self.style['agtime'] = self.style['stime0']
        else:                      self.style['agtime'] = self.style['time0']
            
        # add bold font for headings
        for hdg in ['place','name','age','time','agfactor','agpercent']:
            bhdg = 'b{0}'.format(hdg)
            self.style[bhdg] = copy.deepcopy(self.style[hdg])
            self.style[bhdg].font.bold = True
        
        # this is toggled by self.setbold and understood by the self.set<field> methods
        self.usebold = False
        
    #----------------------------------------------------------------------
    def setbold(self,bold=True):
    #----------------------------------------------------------------------
        '''
        indicate whether text in fields should be bolded
        
        :param bold: True for bold, else False
        '''
        
        self.usebold = bold
        
    #----------------------------------------------------------------------
    def prepare(self,year,racename,orderby):
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
        :param orderby: how results are ordered
        '''
        
        # TODO: add sortby to output file name
        # open output file
        MF = {'F':'Women','M':'Men'}
        rengen = 'Overall'
        if 'gender' in self.resultfilter:
            rengen = MF[self.resultfilter['gender']]
        self.fname = '{0}-{1}-{2}-{3}.xls'.format(year,racename,rengen,orderby)
        self.ws = self.wb.add_sheet('{0}-{1}'.format(rengen,orderby))
        
        # start rendering lines at row 0
        self.rownum = 0
        
        # render race major heading
        resulttype = rengen
        if rengen in MF.values():
            resulttype += "'s"
        OB = {'time':'time','agtime':'adj time','agpercent':'age grade'}
        ob = OB[orderby]
        colnum = 0
        self.ws.write(self.rownum,colnum,"{0} {1} - {2} results, ordered by {3}".format(year,racename,resulttype,ob),self.style['majorhdr'])
        self.rownum += 1
        colnum = 1
        self.ws.write(self.rownum,colnum,"NOTE: these results may have been filtered by club members",self.style['hdr'])
        self.rownum += 2
        
        # set up column numbers -- reset for each series
        self.colnum = {}
        hdrfields = ['place','name','age','time','agfactor','agpercent','agtime']
        for k in hdrfields:
            self.colnum[k] = hdrfields.index(k)

        # set up col widths
        self.ws.col(self.colnum['place']).width = 6*256
        self.ws.col(self.colnum['name']).width = 19*256
        self.ws.col(self.colnum['age']).width = 6*256
        self.ws.col(self.colnum['agpercent']).width = 10*256

        # bold header fields
        self.setbold(True)
        
        self.clearline()
        self.setplace('place')
        self.setname('name')
        self.setage('age')
        self.settime('time')
        self.setagfactor('factor')
        self.setagpercent('age grade')
        self.setagtime('adj time')
        self.render()
        
        # rest of rows are not bold
        self.setbold(False)
    
    #----------------------------------------------------------------------
    def clearline(self):
    #----------------------------------------------------------------------
        '''
        prepare rendering line for output by clearing all entries
        '''
        
        pass    # noop for excel - avoid 'cell overwrite' exception
    
    #----------------------------------------------------------------------
    def setplace(self,place):
    #----------------------------------------------------------------------
        '''
        put value in 'place' column for output (this should be rendered in 1st column)

        :param place: value for place column
        '''
        
        style = self.style['place']
        if self.usebold:
            style = self.style['bplace']
        
        self.ws.write(self.rownum,self.colnum['place'],place,style)
    
    #----------------------------------------------------------------------
    def setname(self,name):
    #----------------------------------------------------------------------
        '''
        put value in 'name' column for output (this should be rendered in 2nd column)

        :param name: value for name column
        '''
        
        style = self.style['name']
        if self.usebold:
            style = self.style['bname']
        
        self.ws.write(self.rownum,self.colnum['name'],name,style)
    
    #----------------------------------------------------------------------
    def setage(self,age):
    #----------------------------------------------------------------------
        '''
        put value in 'age' column for output

        :param age: age on day of race
        '''
        
        style = self.style['age']
        if self.usebold:
            style = self.style['bage']
        
        self.ws.write(self.rownum,self.colnum['age'],age,style)
    
    #----------------------------------------------------------------------
    def settime(self,time):
    #----------------------------------------------------------------------
        '''
        put value in 'time' column for output

        :param time: time (seconds)
        '''
        
        if type(time) in [str,unicode]:
            xltime = time
        else:
            xltime = time / (24*60*60.0)    # convert seconds to days

        # maybe override time style
        timestyle = self.style['time']
        if time >= 60*60:
            timestyle = self.style['time0']
        
        style = timestyle
        if self.usebold:
            # bold isn't numeric so this is ok
            style = self.style['btime']
        
        self.ws.write(self.rownum,self.colnum['time'],xltime,style)
    
    #----------------------------------------------------------------------
    def setagfactor(self,agfactor):
    #----------------------------------------------------------------------
        '''
        put value in 'agfactor' column for output

        :param agfactor: age grade factor (between 0 and 1)
        '''

        style = self.style['agfactor']
        if self.usebold:
            style = self.style['bagfactor']
        
        self.ws.write(self.rownum,self.colnum['agfactor'],agfactor,style)
    
    #----------------------------------------------------------------------
    def setagpercent(self,agpercent):
    #----------------------------------------------------------------------
        '''
        put value in 'agpercent' column for output

        :param agpercent: age grade percentage (between 0 and 100)
        '''
        
        style = self.style['agpercent']
        if self.usebold:
            style = self.style['bagpercent']
        
        self.ws.write(self.rownum,self.colnum['agpercent'],agpercent,style)
    
    #----------------------------------------------------------------------
    def setagtime(self,agtime):
    #----------------------------------------------------------------------
        '''
        put value in 'agtime' column for output

        :param agtime: age grade time (seconds)
        '''
        
        if type(agtime) in [str,unicode]:
            xltime = agtime
        else:
            xltime = agtime / (24*60*60.0)    # convert seconds to days

        # maybe override time style
        timestyle = self.style['time']
        if agtime >= 60*60:
            timestyle = self.style['time0']
        
        style = timestyle
        if self.usebold:
            # bold isn't numeric so this is ok
            style = self.style['btime']
        
        self.ws.write(self.rownum,self.colnum['agtime'],xltime,style)
    
    #----------------------------------------------------------------------
    def render(self):
    #----------------------------------------------------------------------
        '''
        output current line to gender file
        '''

        self.rownum += 1
    
    #----------------------------------------------------------------------
    def skipline(self):
    #----------------------------------------------------------------------
        '''
        output blank line to gender file
        '''

        self.rownum += 1
    
    #----------------------------------------------------------------------
    def close(self):
    #----------------------------------------------------------------------
        '''
        close files associated with this object
        '''
        
        self.wb.save(self.fname)
    
        # kludge to force a new workbook 
        del self.wb
        self.wb = xlwt.Workbook()
        self.rownum = 0

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
        
        # open file, prepare header, etc
        fh.prepare(year,self.racename,self.orderby)
                
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
            fh.settime(result.time)
            fh.setagfactor(result.agfactor)
            fh.setagpercent(result.agpercent)
            fh.setagtime(result.agtime)
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
        fh.addhandler(TxtRaceHandler(session,race.distance,**resultfilter))
        fh.addhandler(XlRaceHandler(session,race.distance,**resultfilter))
        
        # render the results, according to specifications
        rr = RaceRenderer(session,race.name,raceid,orderby,hightolow,**resultfilter)
        rr.renderrace(fh)

    session.close()
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
