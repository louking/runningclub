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

# other
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

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
    datefmt = mdates.DateFormatter('       %b')
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
            ax.annotate(anno[1],anno)

    if debugfile:
        DEB.close()
    
    # add legend and save
    ax.legend(loc=1,bbox_to_anchor=(1.3, 1))    #bbox_to_anchor moves legend outside axes
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
    if overlapfile:
        names = {}

    # input is csv file
    INCSV = csv.DictReader(memberfileh)
    
    # create data structure. will be sorted later
    years = {}
    
    # loop through records.
    for membership in INCSV:
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
            if overlapfile:
                # overlap file is opened later, thisrec keys must match header fields
                thisrec = {'MemberID':memberid,'name':fullname,'renewal':asc_renewaldate,'join':asc_joindate,'expiration':asc_expdate,'dob':dob}
                thisname = (lname,fname,dob)
                if not thisname in names:
                    names[thisname] = []
                names[thisname].append(thisrec)

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
    if overlapfile:
        _OVRLP = open(overlapfile,'wb')
        OVRLP = csv.DictWriter(_OVRLP,['MemberID','name','dob','renewal','join','expiration'])
        OVRLP.writeheader()
        ovrlprecord = 0
        
        for thisname in names.keys():
            if len(names[thisname]) == 1: continue
            datespans = []
            overlap = False
            for rec in names[thisname]:
                thisdatespan = {'join':rec['join'],'expiration':rec['expiration']}
                for datespan in datespans:
                    if (    (datespan['join'] <= thisdatespan['join']       and thisdatespan['join']        <= datespan['expiration']) or
                            (datespan['join'] <= thisdatespan['expiration'] and thisdatespan['expiration']  <= datespan['expiration'])):
                        overlap = True
                        break
                if overlap: break
                datespans.append(thisdatespan)
                
            if overlap:
                OVRLP.writerows(names[thisname])
                
        _OVRLP.close()
        
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
