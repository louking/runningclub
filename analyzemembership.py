#!/usr/bin/python
###########################################################################################
# analyzemembership -- analyze membership year on year
#
#       Date            Author          Reason
#       ----            ------          ------
#       01/15/15        Lou King        Create
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

# standard
import pdb
import argparse
import csv
from datetime import datetime
from calendar import monthrange
from collections import OrderedDict
import time

# home grown
from running.runningaheadmembers import RunningAheadMembers
from loutilities import timeu
ymd = timeu.asctime('%Y-%m-%d')

from . import version

#----------------------------------------------------------------------
def rendermemberanalysis(ordyears,fullmonth,outfile,debugfile=None): 
#----------------------------------------------------------------------
    '''
    :param fullmonth: true if last point is last date of final full month
    :param ordyears: return value from analyzemembership
    :param outfile: output .png file with chart
    :param debugfile: optional summary debug file name
    '''
    
    # only required to render analysis -- removed from module level to allow module on godaddy
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib.dates as mdates
    from matplotlib.font_manager import FontProperties

    # create a figure 
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # format the ticks by month
    months   = mdates.MonthLocator()  # every month
    datefmt = mdates.DateFormatter('        %b')
    ax.xaxis.set_major_formatter(datefmt)
    ax.xaxis.set_major_locator(months)


    # if desired, remove months at end which are not "full months"
    # assumes last date in month is always populated
    if fullmonth:
        lastyear = list(ordyears.keys())[-1]
        lastdate = list(ordyears[lastyear].keys())[-1]
        tempdates = list(ordyears[lastyear].keys())

        # handle all months other than January
        # delete dates that didn't reach the end of the month for the last month in the data
        if lastdate.month > 1:
            while tempdates[-1].day != monthrange(tempdates[-1].year,tempdates[-1].month)[1]:
                del ordyears[lastyear][tempdates[-1]]
                del tempdates[-1]

        # handle case where the lastdate is in January but it's not a full month
        # delete the whole year because that is the same as deleting the partial month of January
        elif tempdates[-1].day != monthrange(tempdates[-1].year,tempdates[-1].month)[1]:
            del ordyears[lastyear]

        # nothing to do if full month of January is in the data
        else:
            pass

    # set up header and size the plots
    # note lastyear may have changed from above if fullmonth and lastdate was in January
    lastyear = list(ordyears.keys())[-1]
    lastdate = list(ordyears[lastyear].keys())[-1]
    fig.suptitle('year on year member count as of {}'.format(ymd.dt2asc(lastdate)))
    fig.subplots_adjust(bottom=0.1, right=0.8, top=0.93)

    #pdb.set_trace()
    if debugfile:
        DEB = open(debugfile,'w')
        DEB.write('date,count\n')
    
    # set up annotation font properties
    annofont = FontProperties(size='small')
    
    # loop each year
    for y in list(ordyears.keys()):
        
        # collect annotations
        annos = []
        annomonth = 0
        annosum = 0
    
        # normalize dates to 2016
        # actual year does not matter -- use 2016 because it is a leap year
        tempdates = list(ordyears[y].keys())
        dates = []
        d0 = tempdates[0]
        lastsum = ordyears[y][d0]
        for d in tempdates:
            normdate = datetime(2016,d.month,d.day)
            dates.append(normdate)
            
            # annotate first day each month with lastsum from previous month
            annosum += ordyears[y][d]
            if debugfile:
                DEB.write('{}-{}-{},{}\n'.format(y,d.month,d.day,annosum))
            while annomonth < d.month:
                annos.append((normdate,lastsum))
                annomonth += 1

            # new lastsum
            lastsum = annosum
        
        # also annotate last date in year
        annos.append((normdate,annosum))

        # get cumulative values
        values = list(ordyears[y].values())
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
        _DETL = open(detailfile,'w',newline='')
        DETL = csv.DictWriter(_DETL,['ord','effective','name','catchup',
                                # 'renewal',
                                'join','expiration'])
        DETL.writeheader()
        detlrecord = 0

    # pull in memberfile
    members = RunningAheadMembers(memberfileh,overlapfile=overlapfile)
    
    # iterate through memberships
    memberships = members.membership_iter()
    
    ## loop through preprocessed records
    years = {}
    for membership in memberships:
        # asc_renewaldate = membership.renew
        asc_joindate = membership.join
        asc_expdate = membership.expiration
        # renewaldate = ymd.asc2dt(asc_renewaldate)
        joindate = ymd.asc2dt(asc_joindate)
        expdate = ymd.asc2dt(asc_expdate)
        fname = membership.fname
        lname = membership.lname
        dob = membership.dob
        fullname = '{}, {}'.format(lname,fname)
        
        # when clicking "Export individual records", joindate is the effective date for the specific year
        effectivedate = joindate
        
        ## increment the member count for the member's effective date
        year = effectivedate.year

        # good data starts in 2013
        if year >= 2013:
            # create year if it hasn't been created
            if year not in years:
                years[year] = {}

            # increment the effectivedate date within the year
            years[year][effectivedate] = years[year].get(effectivedate,0) + 1
            
            # debug
            if detailfile:
                detlrecord += 1
                DETL.writerow({'effective':ymd.dt2asc(effectivedate),'name':fullname,
                               # 'renewal':asc_renewaldate,
                               'join':asc_joindate,'expiration':asc_expdate,
                               'ord':detlrecord})

        # for all years after effectivedate's until expdate's, increment jan 1
        # this happens if there is a grace period and member's renewal counts for following year, 
        # and for multiyear membership
        # NOTE: this is not under "if year >= 2013" because there are some joindates in 2012, 
        # captured here under jan1, 2013
        for y in range(effectivedate.year+1,expdate.year+1):
            jan1 = datetime(y,1,1)
            if y not in years:
                years[y] = {}
            years[y][jan1] = years[y].get(jan1,0) + 1
            
            # debug
            if detailfile:
                detlrecord += 1
                DETL.writerow({'effective':ymd.dt2asc(jan1),'name':fullname,
                               # 'renewal':asc_renewaldate,
                               'join':asc_joindate,'expiration':asc_expdate,
                               'catchup':'y',
                               'ord':detlrecord})
    
    # debug
    if detailfile:
        _DETL.close()
    
    # create an entry with 0 count for today's date, if none exists (use local time)
    # if, say, last entry was July 28, this will have the effect of prettying up the output
    # for full month rendering
    today = timeu.epoch2dt(time.time()-time.timezone)
    thisyear = today.year
    thismonth = today.month
    thisday = today.day
    today = datetime(thisyear, thismonth, thisday)  # removes time of day from today
    if today not in years[thisyear]:
        years[thisyear][today] = 0

    # remove any entries for any years accumulated after this year
    # this can happen if long expiration dates are in database
    for y in range(thisyear+1, max(years.keys())+1):
        years.pop(y)

    # create orderered dicts
    allyears = sorted(list(years.keys()))

    ordyears = OrderedDict()
    for y in allyears:
        ordyears[y] = OrderedDict()

        # make sure each month has entry in first and final date, so annotations in rendermembershipanalysis work nicely
        thismonth = 1
        for thisitem in sorted(list(years[y].items()), key=lambda t: t[0]):
            thisdate = thisitem[0]

            # if we are at a new month, create an empty entry for the first day of this month
            # need while loop in case there was a whole month without memberships
            # also make sure there is an entry the last date of the previous month
            while (thismonth != thisdate.month):
                thismonth += 1

                # make sure there is entry the last date of the previous month
                prevmonth = thismonth - 1
                lastdayprevmonth = monthrange(y,prevmonth)[1]
                lastdateprevmonth = datetime(y,thismonth-1,lastdayprevmonth)
                if lastdateprevmonth not in ordyears[y]:
                    ordyears[y][lastdateprevmonth] = 0

                # make sure there is an entry the first date of this month
                firstdateinmonth = datetime(y,thismonth,1)
                if firstdateinmonth not in ordyears[y]:
                    ordyears[y][firstdateinmonth] = 0
                    
            # add thisitem to ordered dict for year
            ordyears[y][thisitem[0]] = thisitem[1]
        
    return ordyears
    

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    analyze membership
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('-m','--fullmonth',help='if set, final annotation is last date of full month',action='store_true')
    parser.add_argument('-d','--debugfile',help='optional debug file',default=None)
    parser.add_argument('-e','--detailfile',help='optional detailed debug file',default=None)
    parser.add_argument('-o','--overlapfile',help='optional overlap debug file to record overlapping join / expiration date periods',default=None)
    parser.add_argument('memberfile',help='membership file, individual records.  File headers match RunningAHEAD output')
    parser.add_argument('outfile',help='output file (png)')
    args = parser.parse_args()
    
    # analyze data in member file
    IN = open(args.memberfile,'r',newline='')
    ordyears = analyzemembership(IN,args.detailfile,args.overlapfile)
    IN.close()
    
    # render analyzed data
    rendermemberanalysis(ordyears,args.fullmonth,args.outfile,args.debugfile)
    
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
