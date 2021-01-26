'''
rsu_addons - Transform RunSignUp Participant Report for shipping labels
'''
from argparse import ArgumentParser
from csv import DictReader, DictWriter
from logging import getLogger
logger = getLogger(__name__)

# copied from participant file, could be configuration

def main():
    ## these are likely to remain the same
    REGISTRATION = 'Registration ID'
    FIRST = 'First Name'
    LAST = 'Last Name'
    DOB = 'Date of Birth'
    EVENT = 'Event'
    SHIPPINGNAME = 'Shipping Recipient'
    SHIPPINGADDR = 'Shipping Address'
    SHIPPINGCITY = 'Shipping City'
    SHIPPINGSTATE = 'Shipping State'
    SHIPPINGZIP = 'Shipping Zip Code'
    SHIPPINGCOUNTRY = 'Shipping Country'
    shipping_all = [SHIPPINGNAME, SHIPPINGADDR, SHIPPINGCITY, SHIPPINGSTATE, SHIPPINGZIP, SHIPPINGCOUNTRY]
    copyfields = [REGISTRATION, FIRST, LAST, EVENT] + shipping_all

    ## these will most likely change
    ADDONTOTQTY = 'T-Shirt (optional purchase) Total Quantity'
    ADDONOPTIONS = 'T-Shirt (optional purchase): Options'
    GIVEAWAY = 'T-Shirt'
    SHIRTSIZE = 'shirt/size'
    ANNOTATION1 = 'custom ref 1'
    ANNOTATION2 = 'custom ref 2'
    sizes = {
        '': '',
        'No thanks (I have enough shirts)': '',
        'Men\'s Small': 'MS',
        'Men\'s Medium': 'MM',
        'Men\'s Large': 'ML',
        'Men\'s X-Large': 'MXL',
        'Men\'s 2X-Large': 'M2XL',
        'Women\'s XSmall': 'WXS',
        'Women\'s Small': 'WS',
        'Women\'s Medium': 'WM',
        'Women\'s Large': 'WL',
        'Women\'s X-Large': 'WXL',
        'Women\'s 2X-Large': 'W2XL',
        'Youth X-Small': 'YXS',
        'Youth Small': 'YS',
        'Youth Medium': 'YM',
        'Youth Large': 'YL',
        'Youth X-Large': 'YXL',
    }
    eventmap = {
        'Adult Virtual Mile' : 'a',
        'Family Virtual Mile' : 'a',
        'Youth Virtual Mile' : 'a',
        'Miles Challenge' : 'b',
        'Miles and Miles Challenge' : 'c',
    }
    eventmedals = ['Miles Challenge', 'Miles and Miles Challenge']

    parse = ArgumentParser(description="Transform RunSignUp Participant Report for shipping labels")
    parse.add_argument('participants', help="participants report from RunSignUp")
    parse.add_argument('output', help="output shipping list, e.g., for input to pirate ship")
    args = parse.parse_args()

    shipping = {}

    def get_shipping_key(rec):
        return '{}/{}/{}'.format(rec[LAST], rec[FIRST], rec[DOB])

    with open(args.participants, 'r') as infp, open(args.output, 'w', newline='') as outfp:
        inp = DictReader(infp)
        outhdrs = copyfields + [SHIRTSIZE, ANNOTATION1, ANNOTATION2]
        outp = DictWriter(outfp, fieldnames=outhdrs)
        outp.writeheader()

        for inrec in inp:
            first = inrec[FIRST]
            last = inrec[LAST]
            shipping_rc = inrec[SHIPPINGNAME]
            shipping_key = get_shipping_key(inrec)
            if shipping_rc and shipping_key not in shipping:
                shipping[shipping_key] = inrec
            event = inrec[EVENT]
            eventcode = eventmap[event]
            regid = inrec[REGISTRATION]
            label2 = '{} {}'.format(first, last)

            # if receiving a medal, copy record
            if event in eventmedals:
                outrec = {f: inrec[f] for f in copyfields}
                label1 = '{}{}'.format(eventcode, sizes[inrec[GIVEAWAY]])
                outrec[SHIRTSIZE] = inrec[GIVEAWAY]
                outrec[ANNOTATION1] = label1
                outrec[ANNOTATION2] = label2

                if not shipping_rc:
                    for shipfield in shipping_all:
                        outrec[shipfield] = shipping[shipping_key][shipfield]

                outp.writerow(outrec)

            addonqty = int(inrec[ADDONTOTQTY])
            if addonqty > 0:
                if eventcode != 'a':
                    logger.error('seeing addons for {}, reg id {}'.format(event, regid))

                addons = inrec[ADDONOPTIONS].split('\n')
                for addon in addons:
                    outrec = {f: inrec[f] for f in copyfields}
                    label1 = '{}{}'.format(eventcode, sizes[addon])
                    outrec[SHIRTSIZE] = addon
                    outrec[ANNOTATION1] = label1
                    outrec[ANNOTATION2] = label2

                    if not shipping_rc:
                        for shipfield in shipping_all:
                            outrec[shipfield] = shipping[shipping_key][shipfield]

                    outp.writerow(outrec)

if __name__ == "__main__":
    main()
