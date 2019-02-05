''' 
A module to provide data from a specified configuration file. 

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

# An exception raised if any kind of configuration handling error occurs
class ConfException(Exception): pass

class ConfHandler(object):
    def __init__(self, filename='system_settings.ini'):
        ''' Attempt to open a specified ini file for reading. If any errors occur,
        If an error occurs, the 'error' attribute is populated with a string giving details and None is returned. 
        Callers should check if 'error' is non-None, and if so, report the error in an appropriate manner
        ConfException is not raised, to allow the caller to receive a ConfHandler object it can check for the 'error' attribute without
        needing additional exception handling of its own.
        '''
        # open conf parser for specified file
        from ConfigParser import RawConfigParser
        self.conf = RawConfigParser()
        self.error = None
        self.parms = {}
        if not self.conf.read(filename):
            self.error = 'Cannot read ini file %s!' % filename
            return None
        
        # conf file reading fine, store sections list for convenience
        else:
            self.secs = self.conf.sections()

    def read_section(self, sec_title, key, options, non_required=[], optional=False):
        ''' Read the section of the conf file specified by 'sec_title',
        storing the values in the 'parms' attribute, keying by 'key'.
        Raise the ConfException on error, or if any of the items in the 'options'
        list do not appear in the section

        'non_required' is a list of options to process for type, but not to insist on existence of

        'parms' will be a dict of dicts when done, each outer dict keyed by 'key' which holds an inner dict of key-value pairs for a section

        'Each item in 'options' or 'non-required' is a string for the item name or a tuple. 
        If a tuple:  (item name, type of item)
        item types can be 'bool' or 'int'. Anything else is treated as a string
        item type determines how the item is interpreted and what kind of value is placed in the 'parms' dict

        'optional' governs whether an error is returned if the entire section does not exist
        '''
        # Read section details
        if sec_title not in self.secs:
            if not optional:
                self.error = 'There must be a "%s" section in the ini file' % sec_title
                raise ConfException
            else:
                return None

        def make_bool(key, sec, option):
            ''' Attempt to coerce the option of the supplied section into a bool, storing in the parms dict if successful,
            raising a suitable exception if not
            '''
            # read as bool, catching any exception
            try:
                self.parms[key][option] = self.conf.getboolean(sec, option)
            except ValueError:
                self.error = 'The %s option in the "%s" section of the ini file must have a value of "true", "1", "yes", "on", "false", 0, "no" or "off"' % (option, sec)
                raise ConfException

        def make_int(self, key, sec, option):
            ''' Attempt to coerce the option of the supplied section into an int, storing in the parms dict if successful,
            raising a suitable exception if not
            '''
            # read as int, catching any exception
            try:
                self.parms[key][option] = self.conf.getint(sec, option)
            except ValueError:
                self.error = 'The %s option in the "%s" section of the ini file must be an integer' % (option, sec)
                raise ConfException
        

        # Get a dict of parms
        self.parms[key] = {}
        for k,v in self.conf.items(sec_title):
            # store value in current key's dict
            self.parms[key][k] = v
        # step over all options, required and non. Use an enum to permit a length check to know if still in required list
        for num, opt in enumerate(options + non_required, 1):
            # check if opt is a string by checking for an "upper" method, treating it as the only argument if so.
            # Otherwise treat as a tuple of (option name, type)
            if hasattr(opt, 'upper'):
                # treat as a string
                n = opt
                t = 'str'
            else:
                # treat as a tuple
                n = opt[0]
                t = opt[1]

            # Check if n doesn't occur, raising an error if it is not optional
            if n not in self.parms[key].keys():
                if num <= len(options):
                    self.error = 'There must be a %s option in the "%s" section of the ini file' % (n, sec_title)
                    raise ConfException
            else:
                # n does occur, check if it needs coercing
                # check if item type is specified for bool
                if t == 'bool':
                    make_bool(key, sec_title, n)

                # check if item type is specified for int
                if t == 'int':
                    make_int(key, sec_title, n)
            
                # no item type specified, treat as a string. Value is already in dict
                    
