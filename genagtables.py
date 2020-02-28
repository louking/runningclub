#!/usr/bin/python
###########################################################################################
# genagtables - generate tables by age grade with age/distance results
#
#	Date		Author		Reason
#	----		------		------
#       01/29/15        Lou King        Create
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
genagtables - generate tables by age grade with age/distance results
==============================================================================

'''

# standard
import argparse
from collections import OrderedDict
import csv

# home grown
from . import version
from .render import rendertime
from loutilities.agegrade import AgeGrade

# distances in miles
METERSINMILE = 1609.0   # short distance corrects mistake in ag spreadsheet
DISTTBL = OrderedDict([
                    ('5kmRoad',5000/METERSINMILE),
                    ('6kmRoad',6000/METERSINMILE),
                    ('4MileRoad',4.0),
                    ('8kmRoad',8000/METERSINMILE),
                    ('5MileRoad',5.0),
                    ('10kmRoad',10000/METERSINMILE),
                    ('12km',12000/METERSINMILE),
                    ('15km',15000/METERSINMILE),
                    ('10Mile',10.0),
                    ('20km',20000/METERSINMILE),
                    ('Half Mar',13.1),  # short distance corrects mistake in ag spreadsheet
                    ('25km',25000/METERSINMILE),
                    ('30km',30000/METERSINMILE),
                    ('Marathon',26.2)  # short distance corrects mistake in ag spreadsheet
                ])
GEN = {'m':'Male','M':'Male','f':'Female','F':'Female'}

#----------------------------------------------------------------------
def genagtables(gen,agpcs,ages): 
#----------------------------------------------------------------------
    '''
    generate tables by age grade with age/distance results, into current directory
    
    :param gen: gender 'M' or 'F'
    :param agpcs: list of age grade percentages
    :param ages: list of ages
    '''
    
    # instantiate age grade object
    ag = AgeGrade()
    
    # generate csv file for each age grade percentage
    for agpc in agpcs:
        # open file and output heading rows
        fn = 'results-for-age-grade-{}-{}.csv'.format(gen,agpc)
        F = open(fn,'w',newline='')
        F.write('Required Results for Age Grade {} {}%\n'.format(GEN[gen],agpc))
        F.write('\n')
        hdr = ['age'] + list(DISTTBL.keys())
        C = csv.DictWriter(F,hdr)
        C.writeheader()
        
        # generate a row for each age
        for age in ages:
            row = {}
            row['age'] = age
            
            # generate each result
            for dist in list(DISTTBL.keys()):
                # if this fails, need to copy result from runningclub.agegrade to loutilities.agegrade
                thistime = rendertime(ag.result(age,gen,DISTTBL[dist],agpc),0, useceiling=False, usefloor=True)
                
                # make sure format is h:m:s
                while len(thistime.split(':')) < 3:
                    thistime = '0:' + thistime
                
                row[dist] = thistime
                
            C.writerow(row)
            
        # close file
        F.close()
        
#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    generate tables by age grade with age/distance results, into current directory
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('gender',help='gender, "M" or "F"')
    parser.add_argument('agpcrange',help='range of age grade percentages to generate result for "agpcfirst-agpclast"')
    parser.add_argument('agerange',help='range of ages to generate result for "agefirst-agelast"')
    parser.add_argument('-s','--step',help='step between ages, default 1 year',type=int,default=1)
    args = parser.parse_args()
    
    agpcrange = [int(agpc) for agpc in args.agpcrange.split('-')]
    agerange = [int(age) for age in args.agerange.split('-')]
    
    # TBD - add error checking for agpcrange and agerange

    agpcs = list(range(agpcrange[0],agpcrange[1]+1))
    ages = list(range(agerange[0],agerange[1]+args.step, args.step))
    
    genagtables(args.gender,agpcs,ages)
    
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
