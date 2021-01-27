'''
mailchimp_contactactivity - report on activity for mailchimp contacts
'''

# standard
import logging
import argparse
from hashlib import md5
import json
from csv import DictWriter

# pypi
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

# homegrown
from loutilities.transform import Transform
from loutilities.configparser import getitems

class parameterError(Exception): pass

logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# parent = __file__.split('/')[-2]
# module = __file__.split('/')[-1][:-3]
# thislogger = logging.getLogger('{}.{}'.format(parent, module))
thislogger = logging.getLogger(__name__)


def contact_activity(configfile, output, debug=False, requests=False):
    '''
    calculate contact activity dates

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
    :param output: name of output file
    :param debug: set to True for debug output
    :param requests: set to True for requests output (INFO)
    '''

    # set up logging
    thislogger.propagate = True
    if debug:
        # set up debug logging
        thislogger.setLevel(logging.DEBUG)
    elif requests:
        # INFO logging
        thislogger.setLevel(logging.INFO)
    else:
        # WARNING logging
        thislogger.setLevel(logging.WARNING)

    # load configuration
    mcconfig = getitems(configfile, 'mailchimp')
    mckey = mcconfig['MC_KEY']
    mclist = mcconfig['MC_LIST']
    mctimeout = float(mcconfig['MC_TIMEOUT'])

    # download categories / groups from MailChimp
    client = MailChimp(mc_api=mckey, timeout=mctimeout)
    lists = client.lists.all(get_all=True, fields="lists.name,lists.id")
    list_id = [lst['id'] for lst in lists['lists'] if lst['name'] == mclist][0]
    categories = client.lists.interest_categories.all(list_id=list_id,fields="categories.title,categories.id")

    # club member status is kept under Hidden Attributes category
    hidden_id = [c['id'] for c in categories['categories'] if c['title'] == 'Hidden Attributes'][0]
    hiddengroups = client.lists.interest_categories.interests.all(list_id=list_id, category_id=hidden_id,
                                                                  fields="interests.name,interests.id")
    interest = {}
    for hiddengroup in hiddengroups['interests']:
        interest[hiddengroup['name']] = hiddengroup['id']
    member_groups = interest.keys()

    # name fields are in 'merge_fields' key
    merge_fields = 'FNAME,LNAME'.split(',')

    # copy some fields from member record
    member_fields = 'email_address,member_rating,status'.split(',')

    # here we go
    thislogger.info('start')

    # define header
    header = merge_fields[:]
    header += 'email_address,status,campaign date,campaign title,last open,member_rating'.split(',')
    header += member_groups
    with open(output, 'w', newline='') as OUTF:
        OUT = DictWriter(OUTF, header)
        OUT.writeheader()

        # process all members in chunks to save memory
        CHUNK = 500
        offset = 0
        numprocessed = 0
        more = True
        while more:
            # get chunk of members
            membersrec = client.lists.members.all(list_id, count=CHUNK, offset=offset)

            # filter to subscribed members
            members = [m for m in membersrec['members'] if m['status'] == 'subscribed']
            thislogger.info('retrieved {}/{} records, {} are subscribed'.format(
                len(membersrec['members']), membersrec['total_items'], len(members)))
            for member in members:
                thislogger.debug('processing {} {}'.format(numprocessed, member['email_address']))
                numprocessed += 1
                outrec = {}
                for f in member_fields:
                    outrec[f] = member[f]
                for f in merge_fields:
                    outrec[f] = member['merge_fields'][f]

                # get last 50 of member activities
                activities = client.lists.members.activity.all(list_id, member['id'])['activity']

                # search activities from tail for last sent
                for i in range(len(activities)-1, 0, -1):
                    activity = activities[i]
                    if activity['action'] == 'sent':
                        outrec['campaign date'] = activity['timestamp'][0:10]
                        outrec['campaign title'] = activity['title']
                        break

                # search from the beginning for most recent open
                outrec['last open'] = ''
                for activity in activities:
                    if activity['action'] == 'open':
                        outrec['last open'] = activity['timestamp'][0:10]
                        break

                # pull member_group information from member interests
                for g in member_groups:
                    id = interest[g]
                    outrec[g] = ''
                    if member['interests'][id]:
                        outrec[g] = 'yes'

                OUT.writerow(outrec)


            # any more?
            more = len(membersrec['members']) > 0
            # more = False    # override for first test
            offset += CHUNK

    # we're done
    thislogger.info('finish')

# ----------------------------------------------------------------------
def main():
    # ----------------------------------------------------------------------
    '''
    calculate mailchimp contact activity

    '''
    from runningclub.version import __version__

    parser = argparse.ArgumentParser(prog='runningclub')
    parser.add_argument('configfile', help='configuration filename')
    parser.add_argument('output', help='output filename')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    parser.add_argument('--debug', help='turn on detailed debugging', action='store_true')
    parser.add_argument('--requests', help='turn on request', action='store_true')
    args = parser.parse_args()

    # import membership
    contact_activity(args.configfile, args.output, debug=args.debug, requests=args.requests)

# ##########################################################################################
#   __main__
# ##########################################################################################
if __name__ == "__main__":
    main()
