'''
Copyright (c) 2011, Kim van Wyk 
All rights reserved.  

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer. 
Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
from django.core.exceptions import ValidationError
import common_modules
# -----------------------------------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------------------------------
def get_model(obj):
    ''' return the model from the obj, using a dict mapping if one exists, falling
    back onto a capitalized name otherwise
    '''
    d = {'merch_centre':'MerchCentre', 'dist_office':'DistrictOffice', 'brightsight': 'BrightSightOffice'}
    # get the model from the supplied obj
    return getattr(common_modules.models, d.get(obj, obj.capitalize()))

def get_label(obj):
    ''' return a suitable label from the obj, splitting all words at '_' and capitalizing each word.
    First look up if a special name applies for the obj
    '''
    d = {'struct':'District or MD', 'dist_office':'District Office'}
    return d.get(obj, ' '.join(o.capitalize() for o in obj.split('_')))

def validate_phone(value):
    ''' Validate that a phone number is of the form +dd (ddd) ddd dddd
    '''
    import re
    pattern = re.compile(r'''\+\d{1,3}   # the country code, 1 to 3 digits
\ \(\d+\)    # at least 1 digit in braces for an area code
\ \d{1,4}    # First number part, between 1 and 4 digits
\ \d{1,4}    # Second number part, between 1 and 4 digits''', re.VERBOSE)
    if not pattern.search(value):
        raise ValidationError('Please enter phone numbers as "+27 (031) 123 4567", for eg')
