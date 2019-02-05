''' Supply a suitable dictionary for use in Django's ORM
and settings.py file. Only the db settings are supplied,
to allow other modules to use the Django ORM without all of Django

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

# Attempt to read the db_settings.ini file from the directory this file is in
import ConfigParser 
import os
import os.path
FN = os.path.abspath(os.path.join(os.path.split(__file__)[0], 'db_settings.ini'))

print os.getcwd()
def get_db_dict():
    ''' Read db settings from file 'fn' and return a Django-suitable
    dict of database settings
    '''
    # read in username and password for db access from db_settings.ini in local dir
    conf = ConfigParser.RawConfigParser()
    fh = open(FN, 'r')
    conf.readfp(fh)

    d = {
        'default': {
            'ENGINE': 'django.db.backends.%s' % conf.get('DB', 'db_type'),
            'NAME': conf.get('DB', 'schema'),
            'USER': conf.get('DB', 'username'),
            'PASSWORD': conf.get('DB', 'password'),
            'HOST': conf.get('DB', 'host'),
            'PORT': conf.get('DB', 'port')
            }
        }

    fh.close()
    return d
