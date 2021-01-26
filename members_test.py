'''
members_test: only for testing running.runsignup.ClubMemberships
'''

# standard
import logging
import argparse
from hashlib import md5
from datetime import datetime, timedelta
from csv import DictWriter, DictReader
from os.path import join

# pypi

# homegrown
from running.runsignup import RunSignUp, ClubMemberships
from loutilities.transform import Transform
from loutilities.configparser import getitems
from loutilities.timeu import asctime


class parameterError(Exception): pass


thislogger = logging.getLogger("runningclub.mailchimpimport_rsu")

isodate = asctime('%Y-%m-%d')


#######################################################################
class Obj(object):
    '''
    just an object for saving attributes

    give str function
    '''

    # ----------------------------------------------------------------------
    def __str__(self):
        # ----------------------------------------------------------------------
        result = '<{}\n'.format(self.__class__.__name__)
        for key in list(vars(self).keys()):
            result += '   {} : {}\n'.format(key, getattr(self, key))
        result += '>'
        return result


#######################################################################
class Stat(Obj):
    '''
    stat object, stats initialized with 0

    :param statlist: list of stat attributes
    '''

    # ----------------------------------------------------------------------
    def __init__(self, statlist):
        # ----------------------------------------------------------------------
        for stat in statlist:
            setattr(self, stat, 0)


# ----------------------------------------------------------------------
def mcid(email):
    '''
    return md5 hash of lower case email address

    :param email: email address
    :rtype: md5 hash of email address
    '''
    h = md5()
    h.update(email.lower())
    return h.hexdigest()


# ----------------------------------------------------------------------
def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.

    :param dict_args: any number of dicts
    :rtype: merged dict
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


# ----------------------------------------------------------------------
def importmembers(configfile, debug=False, stats=False):
    '''
    import member data to mailchimp

    configfile must have the following

    [mailchimp]

    RSU_CLUB: <runsignup club_id>
    RSU_KEY: <key from runsignup partnership>
    RSU_SECRET: <secret from runsignup partnership>
    MC_KEY: <api key from MailChimp>
    MC_LIST: <name of list of interest>
    MC_GROUPNAMES: groupname1,groupname2,...
    MC_SHADOWCATEGORY: <name of shadowcategory>
        * shadowcategory groups are used to show desired inclusion but the group itself under other categories can be toggled by subscriber
        * this is used to prevent the recipient from being added back to the group against their wishes
        * if a groupname is not also under shadowcategory, it is only ticked if the subscriber was not present in the list prior to import
        * this category's group names include all of the group names which are reserved for members
    MC_CURRMEMBERGROUP: <name of group which is set for current members>
    MC_PASTMEMBERGROUP: <name of group which is set for current and past members>

    :param configfile: name of configuration file
    :param debug: set to True for debug output
    :param stats: set to True for stats output (INFO)
    '''

    # set up logging
    thislogger.propagate = True
    if debug:
        # set up debug logging
        thislogger.setLevel(logging.DEBUG)
    elif stats:
        # INFO logging
        thislogger.setLevel(logging.INFO)
    else:
        # WARNING logging
        thislogger.setLevel(logging.WARNING)

    # load configuration
    rsuconfig = getitems(configfile, 'runsignup')
    mcconfig = getitems(configfile, 'mailchimp')
    debugconfig = getitems(configfile, 'debug')
    club_id = rsuconfig['RSU_CLUB']
    rsukey = rsuconfig['RSU_KEY']
    rsusecret = rsuconfig['RSU_SECRET']
    debugdir = debugconfig['DEBUG_DIRECTORY']

    # these lists, groups, and categories need to be configured directly in MailChimp
    mcrecentdays = mcconfig['MC_RECENTDAYS']

    # use Transform to simplify RunSignUp format
    xform = Transform({
        'last': lambda mem: mem['user']['last_name'],
        'first': lambda mem: mem['user']['first_name'],
        'email': lambda mem: mem['user']['email'] if 'email' in mem['user'] else '',
        'primary': lambda mem: mem['primary_member'] == 'T',
        'start': 'membership_start',
        'end': 'membership_end',
        'modified': 'last_modified',
    },
        # source and target are dicts, not objects
        sourceattr=False,
        targetattr=False
    )

    # download current member and full member lists from RunSignUp
    # get current members from RunSignUp, transforming each to local format
    # only save one member per email address, primary member preferred
    with RunSignUp(key=rsukey, secret=rsusecret, debug=debug) as rsu:
        # create data structure for current members
        rsumembers = rsu.members(club_id)
        rsucurrmembers = {}
        for rsumember in rsumembers:
            memberrec = {}
            xform.transform(rsumember, memberrec)
            memberkey = memberrec['email'].lower()
            # only save if there's an email address
            # the primary member takes precedence, but if different email for nonprimary members save those as well
            if memberkey and (memberrec['primary'] or memberkey not in rsucurrmembers):
                rsucurrmembers[memberkey] = memberrec

        # look at all members
        rsuallmemberships = rsu.members(club_id, current_members_only='F')

    clubmemberships = ClubMemberships(rsuallmemberships)

    # create debug file with each "found" member on a new row
    dbgfields = ClubMemberships.userfields + ['user_ids', 'mships']
    with open(join(debugdir, 'members.csv'), mode='w', newline='') as dbg:
        writer = DictWriter(dbg, dbgfields)
        writer.writeheader()
        for m in clubmemberships.members():
            mrec = {k:getattr(m, k) for k in dbgfields}
            writer.writerow(mrec)

    # now create debug file from the found member file, based on birth dates
    with open(join(debugdir, 'members.csv'), newline='') as found, open(join(debugdir, 'dobs.csv'), mode='w', newline='') as dob:
        founds = DictReader(found)
        dobs = DictWriter(dob, ['dob', 'count', 'names'])
        dob2members = {}
        for member in founds:
            dob2members.setdefault(member['dob'], [])
            dob2members[member['dob']].append('{}/{}'.format(member['first_name'], member['last_name']))
        # note dob is iso formatted, so direct sort is ok
        thedobs = list(dob2members.keys())
        thedobs.sort()
        dobs.writeheader()
        for thedob in thedobs:
            dobs.writerow({'dob':thedob,
                           'count':len(dob2members[thedob]),
                           'names':', '.join(dob2members[thedob])
                           })

    windowstart = isodate.dt2asc(datetime.today() - timedelta(days=mcrecentdays))
    windowend = isodate.dt2asc(datetime.today() - timedelta(days=1))

    # create recentmemberships by passing through rsuallmemberships, removing
    #   those which expire outside of window
    #   those for which the user's email is for a current member
    recentmemberships = []
    for m in clubmemberships.members():
        lastmship = m.mships[0]
        # skip current members
        if isodate.dt2asc(datetime.today()) < lastmship.membership_end: continue

        # skip members who have email in the current member list
        if m.email.lower() in rsucurrmembers: continue

        # if last membership ended within the window, add it to the list
        if lastmship.membership_end >= windowstart and lastmship.membership_end <= windowend:
            recentmemberships.append(m)

    with open(join(debugdir, 'recent.csv'), mode='w', newline='') as recent:
        writer = DictWriter(recent, ['first', 'last', 'email', 'expiration', 'primary'])
        writer.writeheader()

        for m in recentmemberships:
            lastmship = m.mships[0]
            writer.writerow({'first':m.first_name,
                             'last':m.last_name,
                             'email':m.email,
                             'expiration':lastmship.membership_end,
                             'primary':lastmship.primary_member
                             })

    # calculate and save current members
    currmemberships = ClubMemberships(rsumembers)
    with open(join(debugdir, 'current.csv'), mode='w', newline='') as recent:
        writer = DictWriter(recent, ['email', 'first', 'last', 'expiration', 'primary', 'zipcode'])
        writer.writeheader()

        for m in currmemberships.members():
            lastmship = m.mships[0]
            writer.writerow({'first':m.first_name,
                             'last':m.last_name,
                             'email':m.email,
                             'expiration':lastmship.membership_end,
                             'primary':lastmship.primary_member,
                             'zipcode':lastmship.zipcode,
                             })

    x = 1

# ----------------------------------------------------------------------
def main():
    '''
    import member data to mailchimp

    '''
    from runningclub.version import __version__

    parser = argparse.ArgumentParser(prog='runningclub')
    parser.add_argument('configfile', help='configuration filename')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('--debug', help='turn on requests debugging', action='store_true')
    parser.add_argument('--stats', help='turn on stats display', action='store_true')
    args = parser.parse_args()

    # import membership
    importmembers(args.configfile, debug=args.debug, stats=args.stats)


# ##########################################################################################
#   __main__
# ##########################################################################################
if __name__ == "__main__":
    main()
