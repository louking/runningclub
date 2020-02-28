#!/usr/bin/python
###########################################################################################
# analyzeeventmembers -- analyze membership / event registration proximity
#
#       Date            Author          Reason
#       ----            ------          ------
#       04/11/15        Lou King        Create
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
from datetime import datetime, date
from collections import OrderedDict
import time

# other
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties

# home grown
from running.runningaheadmembers import RunningAheadMembers
from running.runningaheadparticipants import RunningAheadParticipants
from loutilities import timeu
from . import version

ymd = timeu.asctime('%Y-%m-%d')
mdy = timeu.asctime('%m/%d/%Y')
MAXDELTA = 28   # 4 weeks

#----------------------------------------------------------------------
def rendermemberanalysis(ordhist,outfile): 
#----------------------------------------------------------------------
    '''
    :param ordhst: return value from analyzemembership
    :param outfile: output .png file with chart
    '''
    
    # create a figure 
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # format the ticks by month
    #fig.suptitle('number of days from time joined club to time registered')
    fig.subplots_adjust(bottom=0.15, right=0.8, top=0.93)

    # set up annotation font properties
    annofont = FontProperties(size='small')
    
    # collect annotations
    annos = []
    annosum = 0
    annosdone = False

    # loop each day delta
    for dy in list(ordhist.keys()):
        
        # sum annotated text
        annosum += ordhist[dy]

        # annotate every week
        if not annosdone and (dy % 7) == 0:
            annos.append((dy,annosum))

        # capture index when dy is at MAXDELTA
        if dy == MAXDELTA:
            lastindex = list(ordhist.keys()).index(dy)
            annosdone = True

    # get cumulative values
    values = list(ordhist.values())[0:lastindex+1]
    cumvalues = np.cumsum(values)
        
    # plot the data
    ax.bar(list(ordhist.keys())[0:lastindex+1], values, label='per day', color='green', edgecolor='none')
    ax.plot(list(ordhist.keys())[0:lastindex+1], cumvalues, label='cumulative')
    for anno in annos:
        ax.annotate(anno[1],anno,fontproperties=annofont)

    # add labels, legend, grid and save
    ax.set_ylabel('count of registrants')
    ax.set_xlabel('#days between joining club and registering for event\n(negative if joined club after registration)')
    ax.legend(loc=1,bbox_to_anchor=(1.3, 0.8))    #bbox_to_anchor moves legend outside axes
    ax.grid(True)
    fig.savefig(outfile,format='png')
        
#----------------------------------------------------------------------
def analyzemembership(memberfileh, participantfileh, detailfile=None): 
#----------------------------------------------------------------------
    '''
    analyze event registration proximity to member joindate
    
    :param memberfileh: membership file handle, individual records
    :param paraticipantfileh: event participant file handle
    :param detailfile: (optional) name of file for detailed output
    :rtype: OrderedDict {numdays: count, ...} - numdays is number of days event registration minus membership join date
    '''
    
    # debug
    if detailfile:
        _DETL = open(detailfile,'w',newline='')
        detailhdr = 'eventname,dob,membername,email,status,joindate,registered,join2event'.split(',')
        DETL = csv.DictWriter(_DETL,detailhdr)
        DETL.writeheader()

    # pull in memberfile, participants file
    membership = RunningAheadMembers(memberfileh)
    event = RunningAheadParticipants(participantfileh)
    
    # iterate through member participants
    participants = event.activeregistrations_iter()

    # what is expiration date for current members
    now = timeu.epoch2dt(time.time())
    currentmemberexp = ymd.dt2asc(datetime(now.year,12,31))
    
    # loop through event registrants, keeping a histogram of how many days since member joined before registering for the event
    # if member joined after registering for the event, the number will be negative
    hist = {}
    for participant in participants:
        # gather event participant information
        lname = participant.lname
        fname = participant.fname
        searchname = '{} {}'.format(fname,lname)
        dob = participant.dob
        asc_regdate = participant.registrationdate  # like '1/28/2015 11:56:53 AM'
        dt_regdate  = mdy.asc2dt(asc_regdate.split(' ')[0])
        asc_regdate = ymd.dt2asc(dt_regdate)        # convert to yyyy-mm-dd
        d_regdate = date(dt_regdate.year, dt_regdate.month, dt_regdate.day)
        email = participant.email

        # create record for detailfile
        detailrec = {'eventname':searchname,'dob':dob,'registered':asc_regdate,'email':email}

        # try to find in member file
        key = membership.getmemberkey(lname,fname,dob)
        if key:
            detailrec['status'] = 'match'

        else:
            closemembers = membership.getclosematchkeys()
            if len(closemembers) >= 1:
                # take best match
                key = closemembers[0]
                detailrec['status'] = 'close'
            else:
                detailrec['status'] = 'missed'
        
        # if found some member who appears to be the right person
        if key:
            # get name of found member
            member = membership.getmember(key)
            membername = '{} {}'.format(member.fname, member.lname)
            detailrec['membername'] = membername
            
            # figure out the join date
            asc_joindate = member.join
            dt_joindate = ymd.asc2dt(asc_joindate)
            d_joindate = date(dt_joindate.year, dt_joindate.month, dt_joindate.day)
            detailrec['joindate'] = asc_joindate

            # check for lapsed members
            if member.expiration != currentmemberexp:
                detailrec['status'] = 'lapsed'

            # how many days since member joined until member registered for event
            join2event = (d_regdate - d_joindate).days
            detailrec['join2event'] = join2event

            # add one to this histogram count
            hist[join2event] = hist.setdefault(join2event,0) + 1

        # debug
        if detailfile:
            DETL.writerow(detailrec)


    # debug
    if detailfile:
        _DETL.close()
        
    # create orderered histogram
    allcounts = sorted(list(hist.keys()))
    ordhist = OrderedDict()
    for y in range(min(allcounts),max(allcounts)+1):
        ordhist[y] = hist[y] if y in hist else 0
        
    return ordhist
    

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    analyze membership
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('memberfile',help='membership file, individual records.  File headers match RunningAHEAD output')
    parser.add_argument('eventfile',help='event file.  File headers match RunningAHEAD output')
    parser.add_argument('outfile',help='output file (png)')
    parser.add_argument('-d','--detailfile',help='detailed output file',default=None)
    args = parser.parse_args()
    
    # analyzed data in member file
    with open(args.memberfile,'r',newline='') as MEMBERS, open(args.eventfile,'r',newline='') as EVENTS:
        ordhist = analyzemembership(MEMBERS, EVENTS, args.detailfile)
    
    # render analyzed data
    rendermemberanalysis(ordhist,args.outfile)
    
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
