#!/usr/bin/python
###########################################################################################
# getresultsmembers -- read results file and determine which members were included
#
#       Date            Author          Reason
#       ----            ------          ------
#       01/21/14        Lou King        Create
#
#   Copyright 2014 Lou King
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
import pdb
import argparse
import csv
from datetime import timedelta
import copy
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s')
logger = logging.getLogger('runningclub.getresultsmembers')

# home grown
from .raceresults import RaceResults, headerError #, dataError
from .clubmember import CsvClubMember
from loutilities import timeu
from loutilities import agegrade
from loutilities.namesplitter import split_full_name
from loutilities.renderrun import rendertime
dbdate = timeu.asctime('%Y-%m-%d')
from . import version

# control behavior of import
DIFF_CUTOFF = 0.7   # ratio of matching characters for cutoff handled by 'clubmember'
AGE_DELTAMAX = 3    # +/- num years to be included in DISP_MISSED
JOIN_GRACEPERIOD = timedelta(7) # allow member to join 1 week beyond race date

# support age grade
ag = agegrade.AgeGrade()

# disposition values
# * match - exact name match found in member table, with age consistent with dateofbirth
# * close - close name match found, with age consistent with dateofbirth
# * missed - close name match found, but age is inconsistent with dateofbirth
# * excluded - this name is in the exclusion table, either prior to import **or as a result of user decision**

DISP_MATCH = 'definite'         # exact match of member 
DISP_CLOSE = 'similar'          # similar match to member, matching age
DISP_MISSED = 'missed'          # similar to some member(s), age mismatch (within window)
DISP_EXCLUDED = 'excluded'      # DISP_CLOSE match, but found in exclusions table
DISP_NOTUSED = 'NOT USED'       # result was not from a member

#----------------------------------------------------------------------
def cleanresult(managedresult):
#----------------------------------------------------------------------
    if not managedresult.name:
        managedresult.name = ' '.join([managedresult.fname,managedresult.lname])
    elif not managedresult.fname or not managedresult.lname:
        names = split_full_name(managedresult.name)
        managedresult.fname = names['fname']
        managedresult.lname = names['lname']
    
    if not managedresult.hometown:
        if managedresult.city and managedresult.state:
            managedresult.hometown = ', '.join([managedresult.city,managedresult.state])

    # gender needs to be upper case
    if managedresult.gender:
        managedresult.gender = managedresult.gender.upper()

#----------------------------------------------------------------------
def filtermissed(missed,racedate,resultage):
#----------------------------------------------------------------------
    '''
    filter missed matches which are greater than a configured max age delta
    also filter missed matches which were in the exclusions table
    
    :param missed: list of missed matches, as returned from clubmember.xxx().getmissedmatches()
    :param racedate: race date in dbdate format
    :param age: resultage from race result, if None, '', 0, empty list is returned
    
    :rtype: missed list, including only elements within the allowed age range
    '''
    # make a local copy in case the caller wants to preserve the original list
    localmissed = missed[:]
    
    # if age in result is invalid, empty list is returned
    if not resultage:
        return []
    
    racedatedt = dbdate.asc2dt(racedate)
    for thismissed in missed:
        # don't consider 'missed matches' where age difference from result is too large
        dobdt = dbdate.asc2dt(thismissed['dob'])
        if abs(timeu.age(racedatedt,dobdt) - resultage) > AGE_DELTAMAX:
            localmissed.remove(thismissed)
        else:
            resultname = thismissed['name']
            runnername = thismissed['dbname']
            ascdob = thismissed['dob']
                
    return localmissed

#----------------------------------------------------------------------
def rendermissed(missed,racedate):
#----------------------------------------------------------------------
    '''
    render missed matches 
    
    :param missed: list of missed matches, as returned from clubmember.xxx().getmissedmatches()
    :param racedate: race date in dbdate format
    
    :rtype: renderable missed list
    '''
    
    racedatedt = dbdate.asc2dt(racedate)
    rtnval = ''
    for thismissed in missed:
        dobdt = dbdate.asc2dt(thismissed['dob'])
        missedage = timeu.age(racedatedt,dobdt)
        rtnval += '{}({}), '.format(thismissed['dbname'],missedage)
        
    if len(rtnval) > 0:
        rtnval = rtnval[:-2]    # remove trailing comma/space
        
    return rtnval

########################################################################
class Member():
########################################################################
    '''
    emulates rrwebapp.raced.Runner (note name change to Member is intended)
    
    :param name: member's name
    :param dateofbirth: yyyy-mm-dd date of birth
    :param gender: M | F
    :param hometown: member's home town
    :param member: True if member (default True)
    :param renewdate: yyyy-mm-dd date of renewal (default None)
    :param expdate: yyyy-mm-dd membership expiration date (default None)
    '''
    
    # make dictionary for attributes which can be directly copied
    fileattrs  = 'Gender,DOB,RenewalDate,ExpirationDate'.split(',')
    classattrs = 'gender,dateofbirth,renewdate,expdate'.split(',')
    file2class = dict(list(zip(fileattrs,classattrs)))
    
    #----------------------------------------------------------------------
    def set(self,filerow):
    #----------------------------------------------------------------------
        '''
        set class attributes based on file row
        '''
        
        for attr in self.fileattrs:
            setattr(self,self.file2class[attr],filerow[attr])
        self.name = ' '.join([filerow['GivenName'],filerow['FamilyName']])
        self.hometown = ', '.join([filerow['City'],filerow['State']])

    #----------------------------------------------------------------------
    def __init__(self, name=None, dateofbirth=None, gender=None, hometown=None, member=True, renewdate=None, expdate=None, fname=None, lname=None):
    #----------------------------------------------------------------------
        try:
            if renewdate:
                dobtest = t.asc2dt(renewdate)
            # special handling for renewdate = None
            else:
                renewdate = ''
        except ValueError:
            raise parameterError('invalid renewdate {0}'.format(renewdate))
        
        self.name = name    
        self.fname = fname    
        self.lname = lname    
        self.dateofbirth = dateofbirth
        self.gender = gender
        self.hometown = hometown
        self.renewdate = renewdate
        self.expdate = expdate
        self.member = member
        self.active = True
        
    #----------------------------------------------------------------------
    def __repr__(self):
    #----------------------------------------------------------------------
        reprval = '{}('.format(self.__class__)
        for attr in dir(self):
            if attr[0:2] == '__' or attr == 'fields': continue
            reprval += '{}={},'.format(attr,getattr(self,attr))
        reprval = reprval[:-1]  #remove trailing comma
        reprval += ')'
        return reprval
    
########################################################################
class Members():
########################################################################
    '''
    abstracts a file containing member information
    
    :param memberscsv: csv file containing member information
    '''
    
    #----------------------------------------------------------------------
    def __init__(self, memberscsv):
    #----------------------------------------------------------------------
        # prepare to read file
        MBR_ = open(memberscsv,'r',newline='')
        MBR = csv.DictReader(MBR_)
        
        # make access to member record easy
        self.members = {}
        for filerow in MBR:
            member = Member()
            member.set(filerow)
            self.members[member.name,member.dateofbirth] = member
        
        # done with file
        MBR_.close()
        
    #----------------------------------------------------------------------
    def find(self, name, dob):
    #----------------------------------------------------------------------
        if (name,dob) in self.members:
            return self.members[name,dob]
        else:
            return None

########################################################################
class ManagedResult():
########################################################################
    '''
    emulates rrwebapp.racedb.ManagedResult
    
    Raw results from original official results, annotated with user's
    disposition about whether each row should be included in standings
    results, which are recorded in :class:`RaceResult`
    
    disposition
    
    * exact - exact name match found in member table, with age consistent with dateofbirth
    * close - close name match found, with age consistent with dateofbirth
    * missed - close name match found, but age is inconsistent with dateofbirth
    * excluded - this name is in the exclusion table, either prior to import or as a result of user decision
    '''
    fields = 'place,name,fname,lname,gender,age,hometown,time,disposition,confirmed'.split(',')

    #----------------------------------------------------------------------
    def __init__(self, place=None,
                 name=None,fname=None,lname=None,
                 gender=None,age=None,
                 city=None,state=None,hometown=None,
                 time=None,
                 disposition=None,
                 confirmed=None):
    #----------------------------------------------------------------------
        self.place = place
        self.name = name
        self.fname = fname
        self.lname = lname
        self.gender = gender
        self.age = age
        self.city = city
        self.state = state
        self.hometown = hometown
        self.time = time
        self.disposition = disposition
        self.confirmed = confirmed

    #----------------------------------------------------------------------
    def __repr__(self):
    #----------------------------------------------------------------------
        reprval = '{}('.format(self.__class__)
        for attr in dir(self):
            if attr[0:2] == '__' or attr == 'fields': continue
            reprval += '{}={},'.format(attr,getattr(self,attr))
        reprval = reprval[:-1]  #remove trailing comma
        reprval += ')'
        return reprval
    
#----------------------------------------------------------------------
def getresultsmember(memberfile,resultsfile,racedate,dist,outfile):
#----------------------------------------------------------------------
    '''
    read a results file and a member file and determine which members
    ran the race
    
    :param memberfile: member file, as output from RunningAHEAD
    :param resultsfile: race results file
    :param dist: distance in miles
    :param racedate: date of race, yyyy-mm-dd format
    :param outfile: output file containing members who ran the race, with confidence level
    '''
    rr = RaceResults(resultsfile,dist)
    
    # get member pool from member file, abstract fill member information
    pool = CsvClubMember(memberfile,cutoff=DIFF_CUTOFF)
    members = Members(memberfile)
    
    # ready output file
    with open(outfile,'w',newline='') as MR_:
        addlfields = 'rendertime,dbname,dbhometown,dbmissed'.split(',')
        allfields = ManagedResult.fields + addlfields
        MR = csv.DictWriter(MR_,allfields,extrasaction='ignore')
        MR.writeheader()
            
        # collect results from resultsfile
        numentries = 0
        mngresults = []
        membersonly = True  # code copied from rrwebapp, make compatible
        while True:
            try:
                fileresult = next(rr)
                mngresult   = ManagedResult()
                for field in fileresult:
                    if hasattr(mngresult,field):
                        setattr(mngresult,field,fileresult[field])
                cleanresult(mngresult)
                logger.debug('Processing {}'.format(mngresult.name))
                
                # create initial disposition
                candidate = pool.findmember(mngresult.name,mngresult.age,racedate)
                logger.debug('  candidate = {}'.format(candidate))
    
                # for members or people who were once members, set age based on date of birth in database
                # note this clause will be executed for membersonly races
                if candidate:
                    # note some candidates' ascdob may come back as None (these must be nonmembers because we have dob for all current/previous members)
                    membername,ascdob = candidate
                    
                    # set active or inactive member's id
                    member = members.find(membername,ascdob)
                
                    # if candidate has renewdate and did not join in time for member's only race, indicate this result isn't used
                    if membersonly and member.renewdate and dbdate.asc2dt(member.renewdate) > dbdate.asc2dt(racedate)+JOIN_GRACEPERIOD:
                            # discard candidate
                            candidate = None
                            
                    # member joined in time for race, or not member's only race
                    # if exact match, indicate we have a match
                    elif membername.lower() == mngresult.name.lower():
                        # if current or former member
                        if ascdob:
                            mngresult.disposition = DISP_MATCH
                            mngresult.confirmed = True
                            logger.debug('    DISP_MATCH')
                            
                        # otherwise was nonmember, included from some non memberonly race
                        # should not happen
                        else:
                            # ignore candidate
                            candidate = None
    
                    # member joined in time for race, or not member's only race, but match wasn't exact
                    else:
                        mngresult.disposition = DISP_CLOSE
                        mngresult.confirmed = False
                        logger.debug('    DISP_CLOSE')
                            
                # didn't find member on initial search, or candidate was discarded
                if not candidate:
                    # favor active members, then inactive members
                    # note: nonmembers are not looked at for missed because filtermissed() depends on DOB
                    missed = pool.getmissedmatches()
                    logger.debug('  pool.getmissedmatches() = {}'.format(missed))
                    
                    # don't consider 'missed matches' where age difference from result is too large, or excluded
                    logger.debug('  missed before filter = {}'.format(missed))
                    missed = filtermissed(missed,racedate,mngresult.age)
                    logger.debug('  missed after filter = {}'.format(missed))
    
                    # if there remain are any missed results, indicate missed (due to age difference)
                    # or missed (due to new member proposed for not membersonly)
                    if len(missed) > 0 or not membersonly:
                        mngresult.disposition = DISP_MISSED
                        mngresult.confirmed = False
                        logger.debug('    DISP_MISSED')
                        
                    # otherwise, this result isn't used
                    else:
                        mngresult.disposition = DISP_NOTUSED
                        mngresult.confirmed = True
                        logger.debug('    DISP_NOTUSED')
                        
                if mngresult.disposition != DISP_NOTUSED:
                    # addlvals must match addlfields
                    if mngresult.disposition != DISP_MISSED:
                        addlvals = [rendertime(mngresult.time,0),member.name,member.hometown,None]
                    else:
                        addlvals = [rendertime(mngresult.time,0),None,None,rendermissed(missed,racedate)]
                    row = copy.copy(mngresult.__dict__)
                    row.update(dict(list(zip(addlfields,addlvals))))
                    MR.writerow(row)
                
            except StopIteration:
                break
            numentries += 1

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    get members included in results file
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('-l','--log',help='set logging level',default='INFO')
    parser.add_argument('memberfile',help='membership file.  File headers match RunningAHEAD output')
    parser.add_argument('resultsfile',help='results file.  File headers match RunningAHEAD output')
    parser.add_argument('racedate',help='date of the race, yyyy-mm-dd')
    parser.add_argument('distance',help='distance of the race in miles',type=float)
    parser.add_argument('outfile',help='output file (csv)')
    args = parser.parse_args()
    
    # get arguments
    memberfile = args.memberfile
    resultsfile = args.resultsfile
    distance = args.distance
    racedate = args.racedate
    outfile = args.outfile
    
    # set logging level
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level,int):
        raise ValueError('Invalid log level: {}'.format(args.log))
    logger.setLevel(numeric_level)
    
    # get the members which are in the results file
    getresultsmember(memberfile,resultsfile,racedate,distance,outfile)
    
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
