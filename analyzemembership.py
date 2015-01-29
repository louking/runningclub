#!/usr/bin/python
###########################################################################################
# analyzemembership -- analyze membership year on year
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
from datetime import datetime
from collections import OrderedDict
from operator import itemgetter

# other
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties

# home grown
from loutilities import timeu
tYMD = timeu.asctime('%Y-%m-%d')
import version

#----------------------------------------------------------------------
def rendermemberanalysis(ordyears,outfile,debugfile=None): 
#----------------------------------------------------------------------
    '''
    :param ordyears: return value from analyzemembership
    :param outfile: output .png file with chart
    :param debugfile: optional summary debug file name
    '''
    
    # create a figure 
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # format the ticks by month
    months   = mdates.MonthLocator()  # every month
    datefmt = mdates.DateFormatter('        %b')
    ax.xaxis.set_major_formatter(datefmt)
    ax.xaxis.set_major_locator(months)

    lastyear = ordyears.keys()[-1]
    lastdate = ordyears[lastyear].keys()[-1]
    fig.suptitle('year on year member count as of {}'.format(tYMD.dt2asc(lastdate)))
    fig.subplots_adjust(bottom=0.1, right=0.8, top=0.93)

    #pdb.set_trace()
    if debugfile:
        DEB = open(debugfile,'w')
        DEB.write('date,count\n')
    
    # set up annotation font properties
    annofont = FontProperties(size='small')
    
    # loop each year
    for y in ordyears.keys():
        
        # collect annotations
        annos = []
        annoday = 32
        annosum = 0
    
        # normalize dates to 2016
        # actual year does not matter -- use 2016 because it is a leap year
        tempdates = ordyears[y].keys()
        dates = []
        for d in tempdates:
            normdate = datetime(2016,d.month,d.day)
            dates.append(normdate)
            
            # annotate first day in month
            annosum += ordyears[y][d]
            if debugfile:
                DEB.write('{}-{}-{},{}\n'.format(y,d.month,d.day,annosum))
            if d.day < annoday:
                annos.append((normdate,annosum))
            annoday = d.day
        
        # also annotate last date in year
        annos.append((normdate,annosum))

        # get cumulative values
        values = ordyears[y].values()
        cumvalues = np.cumsum(values)
        
        # plot the data
        ax.plot(dates, cumvalues, label=y)
        for anno in annos:
            ax.annotate(anno[1],anno,fontproperties=annofont)

    if debugfile:
        DEB.close()
    
    # add labels, legend, grid and save
    ax.set_ylabel('number of members')
    ax.legend(loc=1,bbox_to_anchor=(1.3, 1))    #bbox_to_anchor moves legend outside axes
    ax.grid(True)
    fig.savefig(outfile,format='png')
        
#----------------------------------------------------------------------
def analyzemembership(memberfileh,detailfile=None,overlapfile=None): 
#----------------------------------------------------------------------
    '''
    compare membership statistics, year on year
    
    :param memberfileh: membership file handle, individual records
    :param detailfile: optional detailed debug file name
    :param overlapfile: optional overlap debug file name to record overlapping join / expiration date periods
    :rtype: OrderedDict {year: OrderedDict {datetime:count,...}, ...}
    '''
    
    # debug
    if detailfile:
        _DETL = open(detailfile,'wb')
        DETL = csv.DictWriter(_DETL,['ord','effective','name','catchup','renewal','join','expiration'])
        DETL.writeheader()
        detlrecord = 0

    # input is csv file
    INCSV = csv.DictReader(memberfileh)
    
    ## preprocess file to remove overlaps between join date and expiration date across records
    # each member's records are appended to a list of records in dict keyed by (lname,fname,dob)
    names = {}
    for membership in INCSV:
        asc_joindate = membership['JoinDate']
        asc_expdate = membership['ExpirationDate']
        fname = membership['GivenName']
        lname = membership['FamilyName']
        dob = membership['DOB']
        memberid = membership['MemberID']
        fullname = '{}, {}'.format(lname,fname)

        # get list of records associated with each member, pulling out significant fields
        thisrec = {'MemberID':memberid,'name':fullname,'join':asc_joindate,'expiration':asc_expdate,'dob':dob,'fullrec':membership}
        thisname = (lname,fname,dob)
        if not thisname in names:
            names[thisname] = []
        names[thisname].append(thisrec)

    #debug
    if overlapfile:
        _OVRLP = open(overlapfile,'wb')
        OVRLP = csv.DictWriter(_OVRLP,['MemberID','name','dob','renewal','join','expiration','tossed'],extrasaction='ignore')
        OVRLP.writeheader()

    # sort list of records under each name, and remove overlaps between records
    for thisname in names:
        #if len(names[thisname]) >= 4:
        #    pdb.set_trace()

        # sort should result so records within a name are by join date within expiration year
        # see http://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python
        names[thisname] = sorted(names[thisname],key=lambda k: (k['expiration'],k['join']))
        toss = []
        for i in range(1,len(names[thisname])):
            # if overlapped record detected, push this record's join date after last record's expiration
            # note this only works for overlaps across two records -- if overlaps occur across three or more records that isn't detected
            # this seems ok as only two record problems have been seen so far
            if names[thisname][i]['join'] <= names[thisname][i-1]['expiration']:
                lastexp_dt = tYMD.asc2dt(names[thisname][i-1]['expiration'])
                thisexp_dt = tYMD.asc2dt(names[thisname][i]['expiration'])
                jan1_dt = datetime(lastexp_dt.year+1,1,1)
                jan1_asc = tYMD.dt2asc(jan1_dt)
                # ignore weird record anomalies where this record duration is fully within last record's
                if jan1_dt > thisexp_dt:
                    toss.append(i)
                    names[thisname][i]['tossed'] = 'Y'
                # debug
                if overlapfile:
                    OVRLP.writerow(names[thisname][i-1])    # this could get written multiple times, I suppose
                    OVRLP.writerow(names[thisname][i])
                # update this record's join dates
                names[thisname][i]['join'] = jan1_asc
                names[thisname][i]['fullrec']['JoinDate'] = jan1_asc
        # throw out anomalous records. reverse toss first so the pops don't change the indexes.
        toss.reverse()
        for i in toss:
            names[thisname].pop(i)
    
    # create new, updated memberships
    memberships = []
    for thisname in names:
        for thismembership in names[thisname]:
            memberships.append(thismembership['fullrec'])
    
    # debug
    if overlapfile:
        _OVRLP.close()

    ## loop through preprocessed records
    years = {}
    for membership in memberships:
        asc_renewaldate = membership['RenewalDate']
        asc_joindate = membership['JoinDate']
        asc_expdate = membership['ExpirationDate']
        renewaldate = tYMD.asc2dt(asc_renewaldate)
        joindate = tYMD.asc2dt(asc_joindate)
        expdate = tYMD.asc2dt(asc_expdate)
        fname = membership['GivenName']
        lname = membership['FamilyName']
        dob = membership['DOB']
        memberid = membership['MemberID']
        fullname = '{}, {}'.format(lname,fname)
        
        # semantics of joindate vs renewal date is different on date of initial bulk load
        #if renewaldate == datetime(2013,11,11):
        #    effectivedate = joindate
        #else:
        #    effectivedate = renewaldate
            
        # when clicking "Export individual records", joindate is the effective date for the specific year
        effectivedate = joindate
        
        # good data starts in 2013
        year = effectivedate.year
        if year >= 2013:
            # create year if it hasn't been created
            if year not in years:
                years[year] = {}
                    
            # increment the effectivedate date within the year
            years[year][effectivedate] = years[year].get(effectivedate,0) + 1
            
            # debug
            if detailfile:
                detlrecord += 1
                DETL.writerow({'effective':tYMD.dt2asc(effectivedate),'name':fullname,
                               'renewal':asc_renewaldate,'join':asc_joindate,'expiration':asc_expdate,
                               'ord':detlrecord})

        # for all years after effectivedate's until expdate's, increment jan 1
        for y in range(effectivedate.year+1,expdate.year+1):
            jan1 = datetime(y,1,1)
            if y not in years:
                years[y] = {}
            years[y][jan1] = years[y].get(jan1,0) + 1
            
            # debug
            if detailfile:
                detlrecord += 1
                DETL.writerow({'effective':tYMD.dt2asc(jan1),'name':fullname,
                               'renewal':asc_renewaldate,'join':asc_joindate,'expiration':asc_expdate,
                               'catchup':'y',
                               'ord':detlrecord})
    
    # debug
    if detailfile:
        _DETL.close()
        
    # create orderered dicts
    allyears = years.keys()
    allyears.sort()
    ordyears = OrderedDict()
    for y in allyears:
        ordyears[y] = OrderedDict(sorted(years[y].items(), key=lambda t: t[0]))
        
    return ordyears
    

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    analyze membership
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('-d','--debugfile',help='optional debug file',default=None)
    parser.add_argument('-e','--detailfile',help='optional detailed debug file',default=None)
    parser.add_argument('-o','--overlapfile',help='optional overlap debug file to record overlapping join / expiration date periods',default=None)
    parser.add_argument('memberfile',help='membership file, individual records.  File headers match RunningAHEAD output')
    parser.add_argument('outfile',help='output file (png)')
    args = parser.parse_args()
    
    # analyzed data in member file
    IN = open(args.memberfile,'rb')
    ordyears = analyzemembership(IN,args.detailfile,args.overlapfile)
    IN.close()
    
    # render analyzed data
    rendermemberanalysis(ordyears,args.outfile,args.debugfile)
    
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
