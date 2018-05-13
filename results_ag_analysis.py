#!/usr/bin/python
###########################################################################################
# resultsaganalysis.py - analyze detailed result file producing age grade spreadsheets
#
#   Date        Author      Reason
#   ----        ------      ------
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
resultsaganalysis.py - analyze detailed result file producing age grade spreadsheets
=======================================================================================
'''

# standard
import argparse
import csv
from os.path import join as pathjoin

# pypi

# github

# home grown
import version
from loutilities.transform import Transform
from loutilities.timeu import asctime, age
from datetime import date
from collections import defaultdict, OrderedDict

# time stuff
tymd = asctime('%Y-%m-%d')

# transform DETAILS file produced by scoretility Results Analysis
xform = Transform(
            {
                'name'      : 'runnername',
                'gender'    : 'gender',
                'age'       : lambda result: age(date.today(), tymd.asc2dt(result['dob'])),
                'distmiles' : 'distmiles',
                'ag'        : lambda result: int(float(result['agpercent'])),
                'year'      : lambda result: tymd.asc2dt(result['racedate']).year
            },
            sourceattr=False,
            targetattr=True)

# # from https://gist.github.com/shenwei356/71dcc393ec4143f3447d
# # from: http://stackoverflow.com/questions/651794/whats-the-best-way-to-initialize-a-dict-of-dicts-in-python
# #----------------------------------------------------------------------
# def ddict():
# #----------------------------------------------------------------------
#     return defaultdict(ddict)

#######################################################################
class Result():
#######################################################################
    pass

#######################################################################
class AgeRange():
#######################################################################
    #----------------------------------------------------------------------
    def __init__(self, rangestr):
    #----------------------------------------------------------------------
        rangedef = rangestr.split(',')
        initrange = tuple([int(x) for x in rangedef[0].split('-')])
        rangedelta = int(rangedef[1])
        lastage = int(rangedef[2])

        self.ranges = OrderedDict([(initrange, '{}-{}'.format(initrange[0], initrange[1]))])
        
        nextage = initrange[1]+1
        while( nextage < lastage ):
            rangestart = nextage
            rangeend   = nextage + rangedelta - 1
            if rangeend >= lastage:
                rangeend = lastage-1
            thisrange = tuple([rangestart, rangeend])
            self.ranges[thisrange] = '{}-{}'.format(thisrange[0], thisrange[1])

            nextage += rangedelta
        
        # last range
        lastrange = tuple([lastage,199])
        self.ranges[lastrange] = '{}+'.format(lastage)

    #----------------------------------------------------------------------
    def __call__(self, age):
    #----------------------------------------------------------------------
        # return the range string associated with this age
        for thisgroup in self.ranges:
            if age in range(thisgroup[0], thisgroup[1]+1):
                return self.ranges[thisgroup]

        # age not found
        return None

    #----------------------------------------------------------------------
    def getranges(self):
    #----------------------------------------------------------------------
        return self.ranges

#----------------------------------------------------------------------
def parsefilter(thisfilter):
#----------------------------------------------------------------------
    '''
    parse integer filter string, returning sorted list

    :param thisfilter: list or range of values, e.g., "69,70,71-75"
    :rtype: sorted list of values represented by thisfilter
    '''
    # TODO: add re to check for errors in input format
    filters = []
    tmp_filters = thisfilter.split(',')
    for thisfilter in tmp_filters:
        limits = thisfilter.split('-')
        thisrange = range(int(limits[0]), int(limits[-1])+1)
        filters += thisrange
    filters.sort()
    return filters

#----------------------------------------------------------------------
def analyze(details, summarybase, mindist, maxdist, yearfilter, agfilter, rangedef): 
#----------------------------------------------------------------------
    '''
    analyze details file producing summary by age grade defined by 
    agfilter

    :param details: input result details file
    :param summarybase: base filename for output summary file(s)
    :param mindist: minimum distance
    :param maxdist: maximum distance
    :param agfilter: list or range of age grades, e.g., "69,70,71-75"
    :param rangedef: initial,delta,final, e.g., 18-24,10,80 means 18-24,25-34,35-44,...,75-79,80+
    '''

    # process filters into lists
    yearfilters = parsefilter(yearfilter)
    agfilters = parsefilter(agfilter)

    # set up age ranges
    agerange = AgeRange(rangedef)

    # open input file
    _DETAILS = open(details,'rb')
    DETAILS = csv.DictReader(_DETAILS)

    # for each gender / agfilter value
    #    save name, age, max age grade >= agfilter value
    # summary = {year: { gender : { agegrade : {agerange: set([runner1, runner2, ...]), ...}, ...}, ... }, ...}
    
    # initialize summary
    summary = {}
    for year in yearfilters:
        summary[year] = {}
        for gender in ['M', 'F']:
            summary[year][gender] = {}
            for ag in agfilters:
                summary[year][gender][ag] = {}
                for thisagerange in agerange.ranges.values():
                    summary[year][gender][ag][thisagerange] = set()

    # each row in DETAILS is a result found during scoretility Results Analyis
    for row in DETAILS:
        result = Result()
        xform.transform(row, result)
        
        if result.distmiles < mindist or result.distmiles > maxdist: continue
        if result.year not in yearfilters: continue
        if result.ag not in agfilters: continue

        thisagerange = agerange(result.age)
        if thisagerange:
            # keep track within this age range
            summary[result.year][result.gender][result.ag][thisagerange] |= {result.name}

    # determine the totals set by ag and details set by ag
    summtotals = {}
    for year in yearfilters:
        summtotals[year] = {}
        for gender in ['M', 'F']:
            summtotals[year][gender] = {}
            for i in range(len(agfilters)):
                ag = agfilters[i]
                thisset = set()
                for thisagerange in agerange.ranges.values():
                    thisset |= summary[year][gender][ag][thisagerange]
                summtotals[year][gender][ag] = thisset

    # quick function for header display
    hdr = lambda ag: '{}+'.format(ag)

    # write summary files
    headers = ['Age Range'] + [hdr(ag) for ag in agfilters]
    for year in yearfilters:
        for gender in ['M', 'F']:
            fname = pathjoin(summarybase, 'summary-{}-{}.csv'.format(year, gender))
            with open(fname, 'wb') as _OUT:
                OUT = csv.DictWriter(_OUT, headers)
                OUT.writeheader()
                for thisagerange in agerange.ranges.values():
                    row = {'Age Range' : thisagerange}
                    for i in range(len(agfilters)):
                        ag = agfilters[i]
                        thisset = set()
                        # count all from this (lowest) ag through highest ag
                        for agi in agfilters[i:]:
                            thisset |= summary[year][gender][agi][thisagerange]
                        row[hdr(ag)] = len(thisset)
                    OUT.writerow(row)

                # TOTALS row
                row = {'Age Range' : 'TOTALS'}
                for i in range(len(agfilters)):
                    ag = agfilters[i]
                    thisset = set()
                    # count all from this (lowest) ag through highest ag
                    for agi in agfilters[i:]:
                        thisset |= summtotals[year][gender][agi]
                    row[hdr(ag)] = len(thisset)
                OUT.writerow(row)

    # get detail sets
    detailset = {}
    for year in yearfilters:
        detailset[year] = {}
        for gender in ['M', 'F']:
            detailset[year][gender] = {}
            for i in range(len(agfilters)):
                ag = agfilters[i]
                detailset[year][gender][ag] = set()
                for agi in agfilters[i:]:
                    detailset[year][gender][ag] |= summtotals[year][gender][agi]

    # write detail files
    headers = [hdr(ag) for ag in agfilters]
    for year in yearfilters:
        for gender in ['M', 'F']:
            fname = pathjoin(summarybase, 'details-{}-{}.csv'.format(year, gender))
            with open(fname, 'wb') as _OUT:
                OUT = csv.DictWriter(_OUT, headers)
                OUT.writeheader()
                # reverse order of age grade processing because higher age grade has smaller set
                # keep track of who we already included so we don't repeat them in a new row
                included = []
                for i in range(len(agfilters)-1,-1,-1):
                    ag = agfilters[i]
                    for name in detailset[year][gender][ag]:
                        # add name to appropriate columns
                        if name not in included:
                            row = {}
                            for agname in range(i+1):
                                row[hdr(agfilters[agname])] = name
                            OUT.writerow(row)
                            included.append(name)

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    descr = '''
    Takes results spreadsheet (csv), and summarizes runners by max age grade
    '''
    
    parser = argparse.ArgumentParser(description=descr,formatter_class=argparse.RawDescriptionHelpFormatter,
                                     version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('details',help='input result details file')
    parser.add_argument('summarybase',help='base directory for output summary and detail files')
    parser.add_argument('yearfilter',help='list or range of years, e.g., "2013,2016-2018"')
    parser.add_argument('agfilter',help='list or range of age grades, e.g., "69,70,71-75"')
    parser.add_argument('rangedef',help='age range definition: initial,delta,final, e.g., 18-24,10,80 means 18-24,25-34,35-44,...,75-79,80+')
    parser.add_argument('--mindist',help='minimum distance', type=float, default=0.0)
    parser.add_argument('--maxdist',help='maximum distance', type=float, default=99999.0)
    args = parser.parse_args()

    analyze(args.details, args.summarybase, args.mindist, args. maxdist, args.yearfilter, args.agfilter. args.rangedef)


# ##########################################################################################
#   __main__
# ##########################################################################################
if __name__ == "__main__":
    main()