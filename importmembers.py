#!/usr/bin/python
###########################################################################################
# importmembers - update club members within database
#
#       Date            Author          Reason
#       ----            ------          ------
#       02/01/13        Lou King        Create
#       04/04/13        Lou King        rename from updatemembers due to glitch in setuptools/windows8
#       05/21/13        Lou King        allow non-members in database to be converted to members
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
importmembers - update club members within database
======================================================

Membership spreadsheet must have at least the following columns:

    * First - first name
    * Last - last name
    * DOB - date of birth
    * Gender - M or F
    * City - hometown city
    * State - hometown state (2 char abbreviation)
    
'''

# standard
import pdb
import argparse

# pypi

# github

# other

# home grown
import version
import clubmember
import racedb
from racedb import dbConsistencyError
from loutilities import timeu

# module globals
tYmd = timeu.asctime('%Y-%m-%d')

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    update club membership information
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('memberfile',help='file with member information')
    parser.add_argument('-r','--racedb',help='filename of race database (default is as configured during rcuserconfig)',default=None)
    parser.add_argument('--debug',help='if set, create updatemembers.txt for debugging',action='store_true')
    args = parser.parse_args()
    
    OUT = None
    if args.debug:
        OUT = open('updatemembers.txt','w')
        
    racedb.setracedb(args.racedb)
    session = racedb.Session()
    
    # get clubmembers from file
    members = clubmember.XlClubMember(args.memberfile)
    
    # get all the member runners currently in the database
    # hash them into dict by (name,dateofbirth)
    allrunners = session.query(racedb.Runner).filter_by(member=True,active=True).all()
    inactiverunners = {}
    for thisrunner in allrunners:
        inactiverunners[thisrunner.name,thisrunner.dateofbirth] = thisrunner
        if OUT:
            OUT.write('found id={0}, runner={1}\n'.format(thisrunner.id,thisrunner))
            
    # make report for new members found with this memberfile
    logdir = os.path.dirname(args.memberfile)
    memberfilebase = os.path.splitext(os.path.basename(args.memberfile)[0])
    newmemlogname = '{0}-newmem.csv'.format(memberfilebase)
    NEWMEM = open(os.path.join(logdir,newmemlogname),'wb')
    NEWMEMCSV = csv.DictWriter(NEWMEM,['name','dob'])
    NEWMEMCSV.writeheader()
        
    # process each name in new membership list
    allmembers = members.getmembers()
    for name in allmembers:
        thesemembers = allmembers[name]
        # NOTE: may be multiple members with same name
        for thismember in thesemembers:
            thisname = thismember['name']
            thisdob = thismember['dob']
            thisgender = thismember['gender']
            thishometown = thismember['hometown']

            # prep for if .. elif below by running some queries
            dbmember = racedb.getunique(session,racedb.Runner,member=True,name=thisname,dateofbirth=thisdob)
            if dbmember is None:
                dbnonmember = racedb.getunique(session,racedb.Runner,member=False,name=thisname)
                # TODO: there's a slim possibility that there are two nonmembers with the same name, but I'm sure we've already
                # bolloxed that up in importresult as there's no way to discriminate between the two
                
                # make report for new members
                NEWMEMCSV.writerow({'name':thisname,'dob':thisdob})
                
            # see if this runner is a member in the database already, or was a member once and make the update
            # add or update runner in database
            # get instance, if it exists, and make any updates
            found = False
            if dbmember is not None:
                thisrunner = racedb.Runner(thisname,thisdob,thisgender,thishometown)
                added = racedb.update(session,racedb.Runner,dbmember,thisrunner,skipcolumns=['id'])
                found = True
                
            # if runner's name is in database, but not a member, see if this runner is a nonmemember which can be converted
            # Check first result for age against age within the input file
            # if ages match, convert nonmember to member
            elif dbnonmember is not None:
                # nonmember came into the database due to a nonmember race result, so we can use any race result to check nonmember's age
                result = session.query(racedb.RaceResult).filter_by(runnerid=dbnonmember.id).first()
                resultage = result.agage
                racedate = tYmd.asc2dt(result.race.date)
                dob = tYmd.asc2dt(thisdob)
                expectedage = racedate.year - dob.year - int((racedate.month, racedate.day) < (dob.month, dob.day))
                # we found the right person
                if resultage == expectedage:
                    thisrunner = racedb.Runner(thisname,thisdob,thisgender,thishometown)
                    added = racedb.update(session,racedb.Runner,dbnonmember,thisrunner,skipcolumns=['id'])
                    found = True
                else:
                    print '{} found in database, wrong age, expected {} found {} in {}'.format(thisname,expectedage,resultage,result)
                    # TODO: need to make file for these, also need way to force update, because maybe bad date in database for result
                    # currently this will cause a new runner entry
            
            # if runner was not found in database, just insert new runner
            if not found:
                thisrunner = racedb.Runner(thisname,thisdob,thisgender,thishometown)
                added = racedb.insert_or_update(session,racedb.Runner,thisrunner,skipcolumns=['id'],name=thisname,dateofbirth=thisdob)
                
            # remove this runner from collection of runners which should be deactivated in database
            if (thisrunner.name,thisrunner.dateofbirth) in inactiverunners:
                inactiverunners.pop((thisrunner.name,thisrunner.dateofbirth))
                
            if OUT:
                if added:
                    OUT.write('added or updated {0}\n'.format(thisrunner))
                else:
                    OUT.write('no updates necessary {0}\n'.format(thisrunner))
    
    # any runners remaining in 'inactiverunners' should be deactivated
    for (name,dateofbirth) in inactiverunners:
        thisrunner = session.query(racedb.Runner).filter_by(name=name,dateofbirth=dateofbirth).first() # should be only one returned by filter
        thisrunner.active = False
        
        if OUT:
            OUT.write('deactivated {0}\n'.format(thisrunner))
        
    session.commit()
    session.close()
    NEWMEM.close()
    
    if OUT:
        OUT.close()
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
