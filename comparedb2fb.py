#!/usr/bin/python
###########################################################################################
# comparedb2fb - compare member database to members of facebook group
#
#       Date            Author          Reason
#       ----            ------          ------
#       07/06/13        Lou King        Create
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
comparedb2fb - compare member database to members of facebook group
================================================================================

Usage::
    TBA
'''

# standard
import pdb
import argparse
import json
import csv
import difflib

# home grown
from . import version
from . import racedb
from . import clubmember

# SequenceMatcher to determine matching ratio, which can be used to evaluate CUTOFF value
sm = difflib.SequenceMatcher()

#----------------------------------------------------------------------
def getratio(a,b):
#----------------------------------------------------------------------
    '''
    return the SequenceMatcher ratio for two strings
    
    :rettype: float in range [0,1]
    '''
    sm.set_seqs(a,b)
    return sm.ratio()

#----------------------------------------------------------------------
def findxtraclose(lista,listb,XTRA,CLOSE=None,typea=None,typeb=None): 
#----------------------------------------------------------------------
    '''
    determine elements in lista which do not have close matches in listb (to XTRA)
    and those which do have close matches (to CLOSE)
    
    :param lista: check this lista for close matches in listb
    :param listb: check this lista for close matches in listb 
    :param XTRA: txt file which has lista elements with no close matches in listb
    :param CLOSE: csv file which has close matches, or None if no plan to save these now
    '''
    
    for ela in lista:
        closematches = difflib.get_close_matches(ela.lower(),listb,cutoff=0.7)
        
        if len(closematches) == 0:
            XTRA.write('{}\n'.format(ela))
        
        elif CLOSE is None:
            continue
        
        else:
            closerow = {}
            for elb in closematches:
                closerow[typea] = ela
                closerow[typeb] = elb
                closerow['ratio'] = getratio(ela,elb)
                CLOSE.writerow(closerow)

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    update club membership information
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('facebookfile',help='file with facebook json information -- output from https://graph.facebook.com/<groupnum>/members')
    parser.add_argument('-c','--cutoff',help='cutoff for close match lookup (default %(default)0.2f)',type=float,default=0.7)
    parser.add_argument('-r','--racedb',help='filename of race database (default is as configured during rcuserconfig)',default=None)
    args = parser.parse_args()
    
    # TBD - change to use facebook api
    FB = open(args.facebookfile)
    
    fbmembers_json = ''
    
    # pull in json data.  skip "comments"
    for line in FB:
        stripped = line.lstrip()
        if len(stripped)==0 or stripped[0] == '#': continue
        fbmembers_json += line
    
    # convert to unicode, ignoring non-ascii characters
    fbmembers_json = str(fbmembers_json,'ascii','ignore')
    
    # convert fbmembers to dict, then to list
    fbmembers_dict = json.loads(fbmembers_json)
    fbmembers = []
    for fbentry in fbmembers_dict['data']:
        fbmembers.append(fbentry['name'].lower())
    
    # get active members, as well as nonmembers
    if args.racedb:
        racedbfile = args.racedb
    else:
        racedbfile = racedb.getdbfilename()
    active = clubmember.DbClubMember(racedbfile,cutoff=args.cutoff,member=True,active=True)
    dbmembers = list(active.getmembers().keys())
    # note dbmembers already lower case
    
    # some stats
    print('number in database = {}'.format(len(dbmembers)))
    print('number on facebook = {}'.format(len(fbmembers)))
    
    # open output files to render members of each list not found in other list
    MATCH = open('comparedb2fb-match.txt','w')
    FBXTRA = open('comparedb2fb-fbbutnotdb.txt','w')
    DBXTRA = open('comparedb2fb-dbbutnotfb.txt','w')
    _CLOSE =  open('comparedb2fb-close.csv','w',newline='')
    CLOSE = csv.DictWriter(_CLOSE,['database','facebook','ratio'])
    CLOSE.writeheader()
    
    # filter out exact matches from both lists
    # loop thru copy of dbmembers list as we'll be changing dbmembers from within the loop
    for dbmember in dbmembers[:]:
        # while used in case there are multiple members in either list of same name
        # there is no way to distinguish between these, so we're just assuming they're the same person (even tho they might not be)
        # TODO: see if there's a way to grab the birthdate from facebook's API.  Even if this is available, not everyone puts in their birth date
        if dbmember in fbmembers:
            MATCH.write('{}\n'.format(dbmember))
            while dbmember in fbmembers:
                fbmembers.remove(dbmember)
            while dbmember in dbmembers:
                dbmembers.remove(dbmember)
    
    # with remaining lists determine names definitely not in other list, and close matches
    findxtraclose(fbmembers,dbmembers,FBXTRA,CLOSE,'facebook','database')
    findxtraclose(dbmembers,fbmembers,DBXTRA,CLOSE,'database','facebook')
    
    # close files
    MATCH.close()
    FBXTRA.close()
    DBXTRA.close()
    _CLOSE.close()
    
###########################################################################################
#	__main__
###########################################################################################
if __name__ == "__main__":
    main()
