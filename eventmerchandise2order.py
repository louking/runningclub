###########################################################################################
# membershipcleanup - clean up membership worksheet for use by RA club membership registration system
#
#       Date            Author          Reason
#       ----            ------          ------
#       08/18/15        Lou King        Create
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
#   WITHORDERS WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###########################################################################################
'''
eventmerchandise2order - create spreadsheet suitable to make order from event participant file
======================================================================================================

Usage::
    
'''
# standard
import pdb
import argparse
import csv

# pypi

# github

# home grown
import version


class parameterError(Exception): pass

#----------------------------------------------------------------------
def main(): 
#----------------------------------------------------------------------
    descr = '''
    Take event participant <merchandise> csv file and create <merchandise>-order csv file
    '''
    
    parser = argparse.ArgumentParser(description=descr,formatter_class=argparse.RawDescriptionHelpFormatter,
                                     version='{0} {1}'.format('runningclub',version.__version__))
    parser.add_argument('merchandisefile',help='name of file containing event participant data from RunningAHEAD')
    args = parser.parse_args()
    merchandisefile = args.merchandisefile

    # check input filename
    if merchandisefile[-4:] != '.csv':
        raise parameterError, 'invalid filename {}, must be .csv file'.format(merchandisefile)

    # open input file, output file, and process them
    with open(merchandisefile,'rb') as _PARTICIPANTS, open('{}-order.csv'.format(merchandisefile[:-4]),'wb') as _ORDERS:
        PARTICIPANTS = csv.DictReader(_PARTICIPANTS)
        outheadings = 'customer,email,product,size,count'.split(',')
        ORDERS = csv.DictWriter(_ORDERS,outheadings)
        ORDERS.writeheader()

        # define mapping of product input headings to output fields
        # TODO: this assumes size is part of the heading -- that could be improved
        products = {}
        for field in PARTICIPANTS.fieldnames:
            if field[:9] == '[ProdItem':
                garbage,prodsize = field.split(']: ')
                prodsize_list = prodsize.split(' (Size: ')
                product = prodsize_list[0]
                size = None
                if len(prodsize_list) > 1:
                    size = prodsize_list[1]
                    # if size ends with ')', remove it
                    if size[-1] == ')':
                        size = size[:-1]
                products[field] = {'product':product, 'size':size}

        # these are the interesting headings from the participants file
        product_fields = products.keys()

        # convert event participants file to order file
        for participant in PARTICIPANTS:
            # go through the input fields which reflect merchandise purchase
            for product_field in product_fields:
                # only parse fields which have data
                if participant[product_field]:
                    orderrec = {}
                    orderrec['customer'] = '{} {}'.format(participant['First Name'],participant['Last Name'])
                    orderrec['email'] = participant['Email']
                    orderrec['product'] = products[product_field]['product']
                    orderrec['size'] = products[product_field]['size']
                    orderrec['count'] = participant[product_field]
                    ORDERS.writerow(orderrec)

    
# ##########################################################################################
#   __main__
# ##########################################################################################
if __name__ == "__main__":
    main()