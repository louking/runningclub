#!/usr/bin/python
###########################################################################################
# racingteamresults - split racing team results spreadsheet into separate results files
#
#	Date		Author		Reason
#	----		------		------
#   07/07/15    Lou King    Create
#
#   Copyright 2015 Lou King
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
agegrade - calculate age grade statistics
===================================================
'''

# standard
import argparse
import csv
import string
import re

# pypi

# github

# home grown
from . import version
from .clubmember import CsvClubMember
from loutilities import timeu
tmdy = timeu.asctime('%m/%d/%Y')
tymd = timeu.asctime('%Y-%m-%d')


class memberError(Exception): pass

###########################################################################################
class Club():
###########################################################################################
    '''
    define a club which has a member list, for lookup of age and gender in splitresults

    :param members: filename of csv file containing members as exported from RunningAHEAD
    '''


    #----------------------------------------------------------------------
    def __init__(self,memberfile): 
    #----------------------------------------------------------------------

        self.members = CsvClubMember(memberfile)

    #----------------------------------------------------------------------
    def splitresults(self, FH, debugfile=None): 
    #----------------------------------------------------------------------
        '''
        split input file into separate output files

        output files are named based on Race, Date fields of input file

        :param FH: DictReader object containing race results
        :param debugfile: name of optional debug file
        '''
        # create debug file if specified
        if debugfile:
            _DEB = open(debugfile, 'w',newline='')
            debughdrs = 'date,race,resname,membername,dob'.split(',')
            DEB = csv.DictWriter(_DEB,debughdrs)
            DEB.writeheader()

        try:
            # fields in destination results file
            resultsfields = 'place,name,gender,age,time'.split(',')

            # only use valid filename characters. See http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
            valid_chars = "-_.() {}{}".format(string.ascii_letters, string.digits)

            # each line produces a separate file
            for race in FH:
                racedate = tymd.dt2asc(tmdy.asc2dt(race['Date']))
                racename = race['Race']
                origfname = '{}-{}.csv'.format(racedate,racename)
                fname = ''.join(c for c in origfname if c in valid_chars)
                with open(fname,'w',newline='') as _RFH:
                    RFH = csv.DictWriter(_RFH,resultsfields)
                    RFH.writeheader()
                    place = 1

                    raceresults = race['Athletes / Results']
                    athleteresults = raceresults.split(', ')
                    for athleteresult in athleteresults:
                        athletetime = athleteresult.split(' (')[0]
                        
                        # find time at the end of the string, one or more digits, any number of :, any number of .
                        ressplit = re.search('(.+)\s(([0-9]+:*.*)+)', athletetime)
                        thisathlete = ressplit.group(1)
                        thistime = ressplit.group(2)

                        # look up athlete's dob and gender
                        member = self.members.getmember(thisathlete)
                        if not member:
                            raise memberError('could not find {} - see race {}'.format(thisathlete, race))
                        bestmember = member['matchingmembers'][0]
                        membername = bestmember['name']
                        membergen  = bestmember['gender'][0]    # just first character
                        memberdob  = bestmember['dob']

                        # debug
                        if debugfile:
                            DEB.writerow(dict(list(zip(debughdrs,[racedate,racename,thisathlete,membername,memberdob]))))

                        # output result
                        age = timeu.age(tymd.asc2dt(racedate),tymd.asc2dt(memberdob))
                        RFH.writerow(dict(list(zip(resultsfields,[place,membername,membergen,age,thistime]))))
                        place += 1

        finally:
            # debug
            if debugfile:
                _DEB.close()

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    descr = '''
    Takes Racing Team Results spreadsheet (csv), and splits into separate results files.
    '''
    
    parser = argparse.ArgumentParser(description=descr,formatter_class=argparse.RawDescriptionHelpFormatter,
                                     version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('memberfile',help='filename for csv file containing member list, as exported from RunningAHEAD')
    parser.add_argument('resultsspreadsheet',help='filename of Racing Team Results spreadsheet')
    parser.add_argument('-d','--debugfile',help='optional debug file',default=None)
    args = parser.parse_args()

    members = Club(args.memberfile)
    _FH = open(args.resultsspreadsheet,'r',newline='')
    FH = csv.DictReader(_FH)
    members.splitresults(FH,args.debugfile)


# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()