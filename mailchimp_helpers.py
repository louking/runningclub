'''
mailchimp_helpers - helper classes and functions for mailchimp scripts
'''
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


def mcid(email):
    '''
    return md5 hash of lower case email address

    :param email: email address
    :rtype: md5 hash of email address
    '''
    h = md5()
    h.update(email.lower())
    return h.hexdigest()


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

