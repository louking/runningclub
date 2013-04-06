#!/usr/bin/python
###########################################################################################
# updatemembers - update club members within database
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
updatemembers - update club members within database
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

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    update club membership information
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('memberfile',help='file with member information')
    parser.add_argument('-r','--racedb',help='filename of race database (default %(default)s)',default='sqlite:///racedb.db')
    parser.add_argument('--debug',help='if set, create updatemembers.txt for debugging',action='store_true')
    args = parser.parse_args()
    
    OUT = None
    if args.debug:
        OUT = open('updatemembers.txt','w')
        
    racedb.setracedb(args.racedb)
    session = racedb.Session()
    
    # get clubmembers from file
    members = clubmember.XlClubMember(args.memberfile)
    
    # get all the runners currently in the database
    # hash them into dict by (name,dateofbirth)
    allrunners = session.query(racedb.Runner).filter_by(active=True).all()
    inactiverunners = {}
    for thisrunner in allrunners:
        inactiverunners[thisrunner.name,thisrunner.dateofbirth] = thisrunner
        if OUT:
            OUT.write('found id={0}, runner={1}\n'.format(thisrunner.id,thisrunner))
    
    # process each name in membership list
    allmembers = members.getmembers()
    for name in allmembers:
        thesemembers = allmembers[name]
        # NOTE: may be multiple members with same name
        for thismember in thesemembers:
            # add or update runner in database
            runner = racedb.Runner(thismember['name'],thismember['dob'],thismember['gender'],thismember['hometown'])
            added = racedb.insert_or_update(session,racedb.Runner,runner,skipcolumns=['id'],name=runner.name,dateofbirth=runner.dateofbirth)
            
            # remove this runner from collection of runners which should be deactivated in database
            #if runner.name == 'Lou King':
            #    pdb.set_trace()
            if (runner.name,runner.dateofbirth) in inactiverunners:
                inactiverunners.pop((runner.name,runner.dateofbirth))
                
            if OUT:
                if added:
                    OUT.write('added or updated {0}\n'.format(runner))
                else:
                    OUT.write('no updates necessary {0}\n'.format(runner))
    
    # any runners remaining in 'inactiverunners' should be deactivated
    for (name,dateofbirth) in inactiverunners:
        thisrunner = session.query(racedb.Runner).filter_by(name=name,dateofbirth=dateofbirth).first() # should be only one returned by filter
        thisrunner.active = False
        
        if OUT:
            OUT.write('deactivated {0}\n'.format(thisrunner))
        
    session.commit()
    session.close()

    if OUT:
        OUT.close()
        
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
