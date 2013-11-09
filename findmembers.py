#!/usr/bin/python
###########################################################################################
#   findmembers - find members from registration list
#
#       Date            Author          Reason
#       ----            ------          ------
#       11/07/13        Lou King        Create
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
findmembers - find members from registration list
==========================================================
'''

# standard
import pdb
import argparse
import collections
import os.path
import csv

# pypi

# github

# other

# home grown
from config import dbConsistencyError
import version
import racedb
import clubmember
import raceresults

#----------------------------------------------------------------------
def checkmembership(session,registrationfile,racedate,excluded,active,FOUNDCSV,MISSEDCSV,CLOSECSV): 
#----------------------------------------------------------------------
    '''
    find club members within registration file
    
    :param session: database session
    :param registrationfile: file containing registration data
    :param racedate: date of race for age verification - yyyy-mm-dd format
    :param excluded: list of racers which are to be excluded from results, regardless of member match
    :param active: active members as produced by clubmember.ClubMember()
    :param FOUNDCSV: filehandle to write found members
    :param MISSEDCSV: filehandle to write log of members which did not match age based on dob in database, if desired (else None)
    :param CLOSECSV: filehandle to write log of members which matched, but not exactly, if desired (else None)
    :rtype: number of entries processed
    '''
    
    # collect registrations from registrationfile -- note distance argument doesn't matter
    rr = raceresults.RaceResults(registrationfile,None,timereqd=False)
    numentries = 0
    results = []
    while True:
        try:
            result = rr.next()
            results.append(result)
        except StopIteration:
            break
        numentries += 1
    
    # loop through registration entries
    for rndx in range(len(results)):
        result = results[rndx]
        
        # skip result which has been asked to be excluded
        if result['name'] in excluded: continue
        
        # looking for members only
        # for these, don't indicate found unless member found
        foundmember = active.findmember(result['name'],result['age'],racedate)
        
        # log member names found, but which did not match birth date
        if MISSEDCSV and not foundmember:
            missed = active.getmissedmatches()
            for thismiss in missed:
                name = thismiss['dbname']
                ascdob = thismiss['dob']
                ratio = thismiss['ratio']
                MISSEDCSV.writerow({'registration name':result['name'],'registration age':result['age'],'database name':name,'database dob':ascdob,'ratio':ratio})
            
        # for members or people who were once members, set age based on date of birth in database
        if foundmember:
            # for members get name, id and gender from database (will replace that which was used in results file)
            name,ascdob = foundmember
            if CLOSECSV and name.strip().lower() != result['name'].strip().lower():
                ratio = clubmember.getratio(result['name'].strip().lower(),name.strip().lower())
                CLOSECSV.writerow({'registration name':result['name'],'registration age':result['age'],'database name':name,'database dob':ascdob,'ratio':ratio})
        
            # record matches
            ratio = clubmember.getratio(result['name'].strip().lower(),name.strip().lower())
            FOUNDCSV.writerow({'registration name':result['name'],'registration age':result['age'],'database name':name,'database dob':ascdob,'ratio':ratio})
            
    # return number of entries processed
    return numentries

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('registrationfile',help='file with race registration information')
    parser.add_argument('racedate',help='date for race')
    parser.add_argument('-e','--excludefile',help='file with list of racers to exclude, same format as "close-<registrationfile>.csv"',default=None)
    parser.add_argument('-c','--cutoff',help='cutoff for close match lookup (default %(default)0.2f)',type=float,default=0.7)
    parser.add_argument('-r','--racedb',help='filename of race database (default is as configured during rcuserconfig)',default=None)
    args = parser.parse_args()
    
    registrationfile = args.registrationfile
    racedate = args.racedate
    excludefile = args.excludefile
    
    # get active and inactive members, as well as nonmembers
    if args.racedb:
        racedbfile = args.racedb
    else:
        racedbfile = racedb.getdbfilename()
    active = clubmember.DbClubMember(racedbfile,cutoff=args.cutoff,member=True,active=True)
    
    # open race database
    racedb.setracedb(racedbfile)
    session = racedb.Session()
    
    # get list of excluded racers from excludefile
    excluded = []
    if excludefile is not None:
        with open(excludefile,'rb') as excl:
            exclc = csv.DictReader(excl)
            for row in exclc:
                excluded.append(row['registration name'])
    
    # set up logging files
    logdir = os.path.dirname(registrationfile)
    registrationfilebase = os.path.basename(registrationfile)
    foundlogname = '{0}-found.csv'.format(os.path.splitext(registrationfilebase)[0])
    FOUND = open(os.path.join(logdir,foundlogname),'wb')
    FOUNDCSV = csv.DictWriter(FOUND,['registration name','registration age','database name','database dob','ratio'])
    FOUNDCSV.writeheader()
    missedlogname = '{0}-missed.csv'.format(os.path.splitext(registrationfilebase)[0])
    MISSED = open(os.path.join(logdir,missedlogname),'wb')
    MISSEDCSV = csv.DictWriter(MISSED,['registration name','registration age','database name','database dob','ratio'])
    MISSEDCSV.writeheader()
    closelogname = '{0}-close.csv'.format(os.path.splitext(registrationfilebase)[0])
    CLOSE = open(os.path.join(logdir,closelogname),'wb')
    CLOSECSV = csv.DictWriter(CLOSE,['registration name','registration age','database name','database dob','ratio'])
    CLOSECSV.writeheader()
    
    # check membership for people within registration file
    numentries = checkmembership(session,registrationfile,racedate,excluded,active,FOUNDCSV,MISSEDCSV,CLOSECSV)
    print '   {0} entries processed'.format(numentries)
    
    # close log entries 
    FOUND.close()
    MISSED.close()
    CLOSE.close()
    
    # and we're through
    session.commit()
    session.close()
    
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()