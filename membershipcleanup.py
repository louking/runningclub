###########################################################################################
# membershipcleanup - clean up membership worksheet for use by RA club membership registration system
#
#       Date            Author          Reason
#       ----            ------          ------
#       10/29/13        Lou King        Create
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
membershipcleanup - clean up membership worksheet for use by RA club membership registration system
======================================================================================================

Usage::
    membershipcleanup.py [-h] [-v] membershipfile
    
        Take <membership> csv file and create <membership>-annotated csv file
    
    
    positional arguments:
      membershipfile  name of file containing membership data
    
    optional arguments:
      -h, --help      show this help message and exit
      -v, --version   show program's version number and exit
      
'''
# standard
import pdb
import argparse
import csv
import os.path
from collections import defaultdict
import datetime

# pypi

# github

# home grown
import version
from loutilities import timeu
timein = timeu.asctime('%m/%d/%Y')  # format for input time
timeout = timeu.asctime('%Y-%m-%d') # format for output time

class parameterError(Exception): pass

#----------------------------------------------------------------------
def getval(value): 
#----------------------------------------------------------------------
    '''
    try to return int, then float, then datetime, and if that doesn't work, just original string
    
    :param value: value to translate
    :rtype: int, datetime or string
    '''
    
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            try:
                return timein.asc2dt(value)
            except ValueError:
                return value
            
    # should never reach here, but just in case
    return value

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    descr = '''
    Take <membership> csv file and create <membership>-annotated csv file
    '''
    
    parser = argparse.ArgumentParser(description=descr,formatter_class=argparse.RawDescriptionHelpFormatter,
                                     version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('membershipfile',help='name of file containing membership data')
    args = parser.parse_args()

    # define output header
    # define mapping data structure hm (header map) to map from input field names to output field names
    #   NOTE: if input field name isn't mentioned, it is the same as output field name
    outhdr = 'MembershipType,FamilyName,GivenName,MiddleName,Gender,DOB,Email,PrimaryMember,JoinDate,ExpirationDate,Street1,Street2,City,State,PostalCode,Country,Telephone'.split(',')
    hm = {}
    hm['First'] = 'GivenName'
    hm['Last'] = 'FamilyName'
    hm['Joined'] = 'JoinDate'
    hm['Address'] = 'Street1'
    hm['Zip'] = 'PostalCode'
    hm['Home Phone'] = 'Telephone'
    hm['Primary'] = 'PrimaryMember'
    
    # open input, output files
    membershipfile = args.membershipfile
    membershiproot,membershipext = os.path.splitext(membershipfile)
    if membershipext.lower() != '.csv':
        raise parameterError, '{}: invalid file extention, must be .csv'.format(membershipfile)
    _IN = open(membershipfile,'rb')
    IN = csv.DictReader(_IN)
    outfile = membershiproot + '-annotated.csv'
    _OUT = open(outfile,'wb')
    OUT = csv.DictWriter(_OUT,outhdr,extrasaction='ignore')
    OUT.writeheader()
    
    # run through file, collecting records into dict indexed by street address
    notedemail = False
    members = defaultdict(lambda: [])
    checkaddress = defaultdict(lambda: [])
    for member in IN:
        outmember = defaultdict(lambda: '')
        for key in member:
            if key == '': continue  # skip empty keys
            outkey = key
            if key in hm:
                outkey = hm[key]
            # override certain values
            value = member[key]
            if outkey in ['DOB','JoinDate','ExpirationDate','Age']:
                value = getval(member[key])
            # remove trailing spaces and commas from email address
            elif outkey == 'Email':
                if len(value) == 0: break
                while value[-1] in ' ,':
                    value = value[0:-1]
            outmember[outkey] = value
        address = ','.join([outmember['Street1'],outmember['Street2'],outmember['City'],outmember['State']])
        if outmember['GivenName'] == '' and outmember['FamilyName'] == '': continue # skip empty records
        
        # check age
        joindate = outmember['JoinDate']
        dob = outmember['DOB']        
        calcage = joindate.year - dob.year - int((joindate.month, joindate.day) < (dob.month, dob.day))
        outmember['calcage'] = calcage
        age = outmember['Age']
        #if calcage != age:
        #    name = ' '.join([outmember['GivenName'],outmember['FamilyName']])
        #    print '{} age calculated as {}, but {} in input sheet'.format(name,calcage,age)

        # update date formats, calculate ExpirationDate
        outmember['DOB'] = timeout.dt2asc(dob)
        outmember['JoinDate'] = timeout.dt2asc(joindate)
        # before October, expiration date is this year
        if joindate.year <= 2012:
            expirationdate = datetime.date(2013,12,31)
        elif joindate.month < 10:
            expirationdate = datetime.date(joindate.year,12,31)
        # October 1 and after, expiration date is the following year
        else:
            expirationdate = datetime.date(joindate.year+1,12,31)
        outmember['ExpirationDate'] = timeout.dt2asc(expirationdate)

        # Country is fixed as US
        outmember['Country'] = 'US'

        # TODO: REMOVE THIS -- for testing only, update email address
        if not notedemail:
            notedemail = True
            print '***NOTE: using real email addresses'
        #    print '***NOTE: making all email addresses into lking@pobox.com'
        #outmember['Email'] = 'lking@pobox.com'
        
        # save this member
        members[address].append(outmember)
        checkaddress[outmember['Street1']].append(outmember)

    # check addresses
    #for streetaddr in checkaddress:
    #    outmembers = checkaddress[streetaddr]
    #    if len(outmembers) == 1: continue
    #    outmember = outmembers[0]
    #    address = ','.join([outmember['Street1'],outmember['Street2'],outmember['City'],outmember['State']])
    #    name = ' '.join([outmember['GivenName'],outmember['FamilyName']])
    #    for outmember in outmembers:
    #        thisaddress = ','.join([outmember['Street1'],outmember['Street2'],outmember['City'],outmember['State']])
    #        if thisaddress != address:
    #            thisname = ' '.join([outmember['GivenName'],outmember['FamilyName']])
    #            print 'address mismatch, {} {} vs {} {}'.format(name,address,thisname,thisaddress)
    
    # generate records, checking age for juniors, choosing primary for Two in Household and Family
    for address in members:
        thesemembers = members[address]
        
        # found single membership?  save MembershipType and write to output file
        if len(thesemembers) == 1:
            thismember = thesemembers[0]
            if thismember['calcage'] < 18:
                thismember['MembershipType'] = 'Junior Individual'
            else:
                thismember['MembershipType'] = 'Individual'
            OUT.writerow(thismember)
    
        # choose primary member oldest seems reasonable
        else:
            decmembers = [(mm['calcage'],mm) for mm in thesemembers]
            decmembers.sort(reverse=True)
            #thesemembers = [mm[1] for mm in decmembers]
            thesemembers = []
            primaryfound = False
            for mm in decmembers:
                thismember = mm[1]
                thesemembers.append(thismember)
                if thismember.get('PrimaryMember') == 'Yes':
                    primaryfound = True
            if not primaryfound:
                thesemembers[0]['PrimaryMember'] = 'Yes'
            
            if len(thesemembers) == 2:
                membertype = 'Two in Household'
            else:
                membertype = 'Family'
                
            for member in thesemembers:
                member['MembershipType'] = membertype
                OUT.writerow(member)
    
    _OUT.close()
    _IN.close()
    
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()