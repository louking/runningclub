###########################################################################################
# mailchimpimport_rsu -- import RunSignUp members to mailchimp
#
#       Date            Author          Reason
#       ----            ------          ------
#       04/27/18        Lou King        Create
#
#   Copyright 2018 Lou King
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
import logging
import argparse
from hashlib import md5
import json

# pypi
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

# homegrown
from running.runsignup import RunSignUp
from loutilities.transform import Transform
from loutilities.configparser import getitems

import version

class parameterError(Exception): pass
thislogger = logging.getLogger("runningclub.mailchimpimport_rsu")

#######################################################################
class Obj(object):
#######################################################################
    '''
    just an object for saving attributes

    give str function
    '''
    #----------------------------------------------------------------------
    def __str__(self):
    #---------------------------------------------------------------------- 
        result = '<{}\n'.format(self.__class__.__name__)
        for key in vars(self).keys():
            result += '   {} : {}\n'.format(key, getattr(self,key))
        result += '>'
        return result
    
#######################################################################
class Stat(Obj):
#######################################################################
    '''
    stat object, stats initialized with 0

    :param statlist: list of stat attributes
    '''
    #----------------------------------------------------------------------
    def __init__(self, statlist):
    #----------------------------------------------------------------------
        for stat in statlist:
            setattr(self, stat, 0)


#----------------------------------------------------------------------
def mcid(email):
#----------------------------------------------------------------------
    '''
    return md5 hash of lower case email address

    :param email: email address
    :rtype: md5 hash of email address
    '''
    h = md5()
    h.update(email.lower())
    return h.hexdigest()

#----------------------------------------------------------------------
def merge_dicts(*dict_args):
#----------------------------------------------------------------------
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

#----------------------------------------------------------------------
def importmembers(configfile, debug=False, stats=False):
#----------------------------------------------------------------------
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
    rsuconfig             = getitems(configfile, 'runsignup')
    mcconfig              = getitems(configfile, 'mailchimp')
    club_id               = rsuconfig['RSU_CLUB']
    rsukey                = rsuconfig['RSU_KEY']
    rsusecret             = rsuconfig['RSU_SECRET']
    mckey                 = mcconfig['MC_KEY']
    mclist                = mcconfig['MC_LIST']
    mcgroupnames          = mcconfig['MC_GROUPNAMES'].split(',')
    mcshadowcategory      = mcconfig['MC_SHADOWCATEGORY']
    mcpastmembergroupname = mcconfig['MC_PASTMEMBERGROUP']
    mccurrmembergroupname = mcconfig['MC_CURRMEMBERGROUP']

    # use Transform to simplify RunSignUp format
    xform = Transform( {
                        'last'     : lambda mem: mem['user']['last_name'],
                        'first'    : lambda mem: mem['user']['first_name'],
                        'email'    : lambda mem: mem['user']['email'] if 'email' in mem['user'] else '',
                        'primary'  : lambda mem: mem['primary_member'] == 'T',
                        'start'    : 'membership_start',
                        'end'      : 'membership_end',
                        'modified' : 'last_modified',
                       },
                       # source and target are dicts, not objects
                       sourceattr=False,
                       targetattr=False
                     )

    # download current member list from RunSignUp
    # get current members from RunSignUp, transforming each to local format
    # only save one member per email address, primary member preferred
    rsu = RunSignUp(key=rsukey, secret=rsusecret, debug=debug)
    rsu.open()

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
    
    rsu.close()

    # It's important not to add someone back to a group which they've decided not to receive 
    # emails from. For this reason, a membergroup is defined with the same group names as
    # the real groups the user is interested in, for those groups which don't make up the whole
    # list.

    
    # download categories / groups from MailChimp
    client = MailChimp(mc_api=mckey, timeout=10.0)
    lists = client.lists.all(get_all=True, fields="lists.name,lists.id")
    list_id = [lst['id'] for lst in lists['lists'] if lst['name'] == mclist][0]
    categories = client.lists.interest_categories.all(list_id=list_id,fields="categories.title,categories.id")
    # groups are for anyone, shadowgroups are for members only
    groups = {}
    shadowgroups = {}
    # for debugging
    allgroups = {}
    for category in categories['categories']:
        mcgroups = client.lists.interest_categories.interests.all(list_id=list_id,category_id=category['id'],fields="interests.name,interests.id")
        for group in mcgroups['interests']:
            # save for debug
            allgroups[group['id']] = '{} / {}'.format(category['title'], group['name'])
            # special group to track past members
            if group['name'] == mcpastmembergroupname:
                mcpastmembergroup = group['id']

            # and current members
            elif group['name'] == mccurrmembergroupname:
                mccurrmembergroup = group['id']

            # newly found members are enrolled in all groups
            elif category['title'] != mcshadowcategory:
                groups[group['name']] = group['id']

            # shadowgroups is used to remember the state of member's only groups for previous members
            # if a member's membership has expired they must be removed from any group(s) which have the same name as 
            # those within the shadowgroup(s) (associated groups)
            # additionally if any nonmembers are found, they must be removed from the associated groups
            # this last bit can happen if someone who is not a member tries to enroll in a members only group
            else:
                shadowgroups[group['name']] = group['id']

    # set up specific groups for mc api
    mcapi = Obj()
    # members new to the list get all the groups
    mcapi.newmember = { id : True for id in groups.values() + shadowgroups.values() + [mccurrmembergroup] + [mcpastmembergroup]}
    # previous members who lapsed get the member groups disabled
    mcapi.nonmember = { id : False for id in [groups[gname] for gname in groups.keys() if gname in shadowgroups] + [mccurrmembergroup] }
    # members groups set to True, for mcapi.unsubscribed merge
    mcapi.member = { id : True for id in shadowgroups.values() + [groups[gname] for gname in groups.keys() if gname in shadowgroups] + [mccurrmembergroup] + [mcpastmembergroup]}
    # unsubscribed members who previously were not past members get member groups turned on and 'other' groups turned off 
    mcapi.unsubscribed = merge_dicts (mcapi.member, { id:False for id in [groups[gname] for gname in groups.keys() if gname not in shadowgroups] })

    # retrieve all members of this mailchimp list
    # key these into dict by id (md5 has of lower case email address)
    tmpmcmembers = client.lists.members.all(list_id=list_id, get_all=True, fields='members.id,members.email_address,members.status,members.merge_fields,members.interests')
    mcmembers = {}
    for mcmember in tmpmcmembers['members']:
        mcmembers[mcmember['id']] = mcmember

    # collect some stats
    stat = Stat(['addedtolist', 'newmemberunsubscribed', 'newmember', 'pastmember', 
                'nonmember', 'memberunsubscribedskipped', 'membercleanedskipped',
                'mailchimperror'])

    # loop through club members
    # if club member is in mailchimp
    #    make sure shadowgroups are set (but don't change groups as these may have been adjusted by club member)
    #    don't change subscribed status
    #    pop off mcmembers as we want to deal with the leftovers later
    # if club member is not already in mailchimp
    #    add assuming all groups (groups + shadowgroups)
    for memberkey in rsucurrmembers:
        clubmember = rsucurrmembers[memberkey]
        mcmemberid = mcid(clubmember['email'])
        thislogger.debug( 'processing {} {}'.format(clubmember['email'], mcmemberid) )

        # if club member is in mailchimp
        if mcmemberid in mcmembers:
            mcmember = mcmembers.pop(mcmemberid)
            # check if any changes are required
            # change required if current member not set
            if not mcmember['interests'][mccurrmembergroup]: 
                # if not past member, just set the needful
                if not mcmember['interests'][mcpastmembergroup]:
                    # if subscribed, all groups are set
                    if mcmember['status'] == 'subscribed':
                        client.lists.members.update(list_id=list_id, subscriber_hash=mcmemberid, data={'interests' : mcapi.newmember})
                        stat.newmember += 1
                    # if unsubscribed, subscribe them to member stuff, but remove everything else
                    elif mcmember['status'] == 'unsubscribed':
                        try:
                            client.lists.members.update(list_id=list_id, subscriber_hash=mcmemberid, data={'interests' : mcapi.unsubscribed, 'status' : 'subscribed'})
                            stat.newmemberunsubscribed += 1
                        # MailChimp won't let us resubscribe this member
                        except MailChimpError as e:
                            thislogger.info('member unsubscribed, skipped: {}'.format(clubmember['email']))
                            stat.memberunsubscribedskipped += 1
                    # other statuses are skipped
                    else:
                        thislogger.info('member cleaned, skipped: {}'.format(clubmember['email']))
                        stat.membercleanedskipped += 1;
                # past member, recall what they had set before for the member stuff
                else:
                    pastmemberinterests = merge_dicts({ groups[gname] : mcmember['interests'][shadowgroups[gname]] for gname in shadowgroups.keys() }, 
                                                      { mccurrmembergroup : True })
                    client.lists.members.update(list_id=list_id, subscriber_hash=mcmemberid, data={'interests' : pastmemberinterests})
                    stat.pastmember += 1

        # if club member is missing from mailchimp
        else:
            try:
                client.lists.members.create(list_id=list_id, 
                                            data={
                                                'email_address' : clubmember['email'],
                                                'merge_fields'  : {'FNAME' : clubmember['first'], 'LNAME' : clubmember['last'] },
                                                'interests'     : mcapi.newmember,
                                                'status'        : 'subscribed'
                                            })
                stat.addedtolist += 1

            except MailChimpError as e:
                ed = e.args[0]
                thislogger.warning('MailChimpError {} for {}: {}'.format(ed['title'], clubmember['email'], ed['detail']))
                stat.mailchimperror += 1

    # at this point, mcmembers have only those enrollees who are not in the club
    # loop through each of these and make sure club only interests are removed
    for mcmemberid in mcmembers:
        mcmember = mcmembers[mcmemberid]
        # change required if current member set
        if mcmember['interests'][mccurrmembergroup]: 
            # save member interests for later if they rejoin
            memberinterests = {shadowgroups[gname]:mcmember['interests'][groups[gname]] for gname in shadowgroups}
            client.lists.members.update(list_id=list_id, subscriber_hash=mcmemberid, data={'interests' : merge_dicts(mcapi.nonmember, memberinterests)})
            stat.nonmember += 1

    # log stats
    thislogger.info ( stat )


#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    '''
    import member data to mailchimp

    '''
    parser = argparse.ArgumentParser(version='{0} {1}'.format('runningclub', version.__version__))
    parser.add_argument('configfile', help='configuration filename')
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
