###########################################################################################
# checkmultimemberships --
#   reads input file [RSU_CACHEFILE]
#   writes output file [RSU_MULTIFILE], showing current multi-person memberships with only one member
#
###########################################################################################

# standard
import argparse
from argparse import ArgumentParser
from csv import DictReader
from datetime import datetime, timedelta
#from collections import OrderedDict
from csv import DictWriter

# pypi

# homegrown
from running.runsignup import RunSignUp, updatemembercache
from loutilities.configparser import getitems

from loutilities import timeu

ymd = timeu.asctime('%Y-%m-%d')
mdy = timeu.asctime('%m/%d/%Y')
md = timeu.asctime('%m-%d')

import version

class parameterError(Exception): pass

# ----------------------------------------------------------------------
def analyzemultimembers(membercachefile, multifile=None):
    # ----------------------------------------------------------------------
    multimembers = {}
    multimemberdata = {}
    multimembersinglecnt = 0

    with open(membercachefile, 'r') as memfile:
        today = datetime.now()
        cachedmembers = DictReader(memfile)
        for memberrec in cachedmembers:
            enddate = ymd.asc2dt(memberrec['ExpirationDate'])

            if (((memberrec['MembershipType'] == "Family") or
                (memberrec['MembershipType'] == "Two in Household") or
                (memberrec['MembershipType'] == "Individual + Junior")) and
                (enddate >= today)):
                if ((memberrec['MembershipID']) in multimembers):
                    multimembers[memberrec['MembershipID']] += 1
                    if ((memberrec['MembershipID']) in multimemberdata):
                        del multimemberdata[memberrec['MembershipID']]
                else:
                    multimembers[memberrec['MembershipID']] = 1
                    multimemberdata[memberrec['MembershipID']] = memberrec

    if multifile:
        with open(multifile, 'w', newline='') as multif:
            cachehdr = 'MemberID,MembershipID,MembershipType,FamilyName,GivenName,MiddleName,Gender,DOB,Email,PrimaryMember,JoinDate,ExpirationDate,LastModified'.split(
                ',')
            cache = DictWriter(multif, cachehdr)
            cache.writeheader()
            for memberid, memberCnt in multimembers.items():
                if memberCnt == 1:
                    multimembersinglecnt += 1
                    # find the member record that corresponds to memberid
                    memberrec = multimemberdata[memberid]
                    if (memberrec):
                        cache.writerow(memberrec)

    return multimembersinglecnt

# ----------------------------------------------------------------------
def summarize(configfile, debug=False):
    # ----------------------------------------------------------------------
    '''
    Summarize the membership stats and members for a given runsignup club.

    :param configfile: configuration filename
    :param debug: True for requests debugging
    '''

    # configuration file supplied -- pull credentials from the app section
    appconfig = getitems(configfile, 'runsignup')
    club = appconfig['RSU_CLUB']
    membercachefile = appconfig['RSU_CACHEFILE']
    memberstatsfile = appconfig['RSU_STATSFILE']
    membermultifile = appconfig['RSU_MULTIFILE']
    key = appconfig['RSU_KEY']
    secret = appconfig['RSU_SECRET']

    # update member cache file
    # note this update is done under lock to prevent any apache thread from disrupting it
#    members = updatemembercache(club, membercachefile, key=key, secret=secret, debug=debug)

    # analyze the memberships for multi-person memberships with only one member
    multicount = analyzemultimembers(membercachefile, multifile=membermultifile)

    # for debugging
    #    return members, memberstats
#    return members, multicount
    return multicount


# ----------------------------------------------------------------------
def main():
    # ----------------------------------------------------------------------
    '''
    update member cache and summarize member statistics

    configfile must have the following

    [runsignup]

    CLUB: <runsignup club_id>
    KEY: '<key from runsignup partnership'
    SECRET: '<secret from runsignup partnership'
    CACHEFILE: 'input/output csv file which caches individual membership dates'
    STATSFILE: 'output json file which will receive daily member count statistics'
    MULTIFILE: 'output csv file with only those multi-person memberships with a single member'
    '''
    #   KC next line getting errors on "version", so re-worked slightly
    #    parser: ArgumentParser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub', version.__version__))
    progVersion = '{0} {1}'.format('runningclub', version.__version__)
    parser: ArgumentParser = argparse.ArgumentParser(progVersion)
    parser.add_argument('configfile', help='configuration filename', default=None)
    parser.add_argument('--debug', help='turn on requests debugging', action='store_true')
    args = parser.parse_args()

    # summarize membership
    summarize(args.configfile, debug=args.debug)


# ##########################################################################################
#   __main__
# ##########################################################################################
if __name__ == "__main__":
    main()
