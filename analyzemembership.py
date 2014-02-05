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
import csv

# home grown
from loutilities import timeu
tYMD = timeu.asctime('%Y-%m-%d')

#----------------------------------------------------------------------
def analyzemembership(directory,files): 
#----------------------------------------------------------------------
    '''
    compare membership statistic, year on year
    
    :param directory: directory for files and output
    :param files: list of files which contain membership data
    '''
    
    membersbymonth = {} # {year:{month:totalmembers,...}...}
    members = {}        # {dob:[{'GivenName':GivenName,'FamilyName':FamilyName},...],...}
    
    
    

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    analyze membership
    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('directory',help='analyze files in this directory')
    parser.add_argument('files',help='list of files, comma separated, no spaces.  File headers match RunningAHEAD output')
    args = parser.parse_args()
    
    directory = args.directory
    files = args.files.split(',')

    analyzemembership(directory,files)
    
# ##########################################################################################
#	__main__
# ##########################################################################################
if __name__ == "__main__":
    main()
