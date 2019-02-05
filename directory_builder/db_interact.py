''' Functions to interact with a DB,
including import and data dumping.

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
from subprocess import call, PIPE
from os.path import exists
import ConfigParser 

class InitNotDone(Exception): pass
class DBTypeNotSupported(Exception): pass
class OperationException(Exception): pass
class MissingParmException(Exception): pass
class BadFileName(Exception): pass

DEBUG = False
HANDLE_EXC = False
# dict to db connection details
DB = {}

def init(ini_file='db_settings.ini'):
    ''' read in username and password for db access from 'ini_file'
    Set parms into DB
    return True on success, raise Exception on error
    '''
    global DB
    if DB:
        return True
    try:
        conf = ConfigParser.RawConfigParser()
        fh = open(ini_file, 'r')
        conf.readfp(fh)

        # obtain required parms from conf file
        # only db type and schema are required
        for parm in ['schema', 'db_type']:
            if not conf.has_option('DB', parm):
                raise MissingParmException                
            DB[parm] = conf.get('DB', parm)

        # obtain optional parms
        for parm in ['username', 'password', 'host']:
            if conf.has_option('DB', parm):
                DB[parm] = conf.get('DB', parm)
        return True

    except ConfigParser.NoOptionError:
        DB = {}
        raise MissingParmException
    except:
        DB = {}
        if not HANDLE_EXC: raise
        raise OperationException
    finally:
        fh.close()
        
def import_data(in_file):
    ''' Import the sql dump in in_file into the current schema
    if able to do so for the current db_type.
    Raise DBTypeNotSupported otherwise.
    Return True on success, OperationException on error
    '''
    global DB
    if not DB:
        raise InitNotDone
    if DB['db_type'] == 'mysql':
        if not exists(in_file):
            raise BadFileName
        ret = call(['mysql', '-u%s' % DB['username'], '-p%s' % DB['password'], '-h%s' % DB['host'], DB['schema'], '<', in_file])
        if ret == 0:
            # all okay
            return True
        raise OperationException
    else:
        # don't know what to do with this db type
        raise DBTypeNotSupported

def dump(out_file, no_data=False):
    ''' Dump the data in the current schema into 'out_file'
    if able to do so for the current db_type.
    Raise DBTypeNotSupported otherwise.
    'no_data' specifies whether to dump just the table structure or to include the data
    Return True on success, OperationException on error
    '''
    global DB
    if not DB:
        raise InitNotDone
    if DB['db_type'] == 'mysql':
        ret = call(['mysqldump', '--add-drop-database', '-v', '-u%s' % DB['username'], '-p%s' % DB['password'], 
                    '-h%s' % DB['host'], no_data and '-d' or '', '-B %s' % DB['schema'], '>', out_file], stdout=PIPE)
        print ret
        if ret == 0:
            # all okay
            return True
        raise OperationException
    else:
        # don't know what to do with this db type
        raise DBTypeNotSupported

if __name__ == "__main__":
    # called from cmd line, set up arg parsing and return codes
    import Enum
    import sys
    RET_CODE = Enum.Enumeration('Return Codes', (('NO_ERROR', 0), 'NO_INIT', 'DB_TYPE_NOT_SUPPORTED', 'OPERATION_ERROR',
                                                 'MISSING_PARM', 'BAD_FILENAME', 'UNKNOWN_ERROR'))

    def exit(code):
        ''' Exit with the supplied code. Print code and Enum if instructed
        '''
        if DEBUG:
            print RET_CODE.whatis(code)
        sys.exit(code)

    def init_wrap(args):
        ''' Call init, interpreting appropriate argparse args
        '''
        try:
            init(ini_file = args.config_file)
            exit(RET_CODE.NO_ERROR)
        except MissingParmException:
            if not HANDLE_EXC: raise
            exit(RET_CODE.MISSING_PARM)
        except OperationException:
            if not HANDLE_EXC: raise
            exit(RET_CODE.OPERATION_ERROR)
        except:
            # all other errors cause an unexpected error
            if not HANDLE_EXC: raise
            exit(RET_CODE.UNKNOWN_ERROR)

    def import_wrap(args):
        ''' Call import, interpreting appropriate argparse args
        '''
        try:
            init(ini_file = args.config_file)
            import_data(args.in_file)
            exit(RET_CODE.NO_ERROR)
        except MissingParmException:
            if not HANDLE_EXC: raise
            exit(RET_CODE.MISSING_PARM)
        except InitNotDone:
            if not HANDLE_EXC: raise
            exit(RET_CODE.NO_INIT)
        except OperationException:
            if not HANDLE_EXC: raise
            exit(RET_CODE.OPERATION_ERROR)
        except DBTypeNotSupported:
            if not HANDLE_EXC: raise
            exit(RET_CODE.DB_TYPE_NOT_SUPPORTED)
        except:
            # all other errors cause an unexpected error
            if not HANDLE_EXC: raise
            exit(RET_CODE.UNKNOWN_ERROR)

    def dump_wrap(args):
        ''' Call dump, interpreting appropriate argparse args
        '''
        try:
            init(ini_file = args.config_file)
            dump(args.out_file, args.no_data)
            exit(RET_CODE.NO_ERROR)
        except InitNotDone:
            if not HANDLE_EXC: raise
            exit(RET_CODE.NO_INIT)
        except OperationException:
            if not HANDLE_EXC: raise
            exit(RET_CODE.OPERATION_ERROR)
        except DBTypeNotSupported:
            if not HANDLE_EXC: raise
            exit(RET_CODE.DB_TYPE_NOT_SUPPORTED)
        except:
            # all other errors cause an unexpected error
            if not HANDLE_EXC: raise
            exit(RET_CODE.UNKNOWN_ERROR)

    import argparse
    # Parse command line args for required files
    parser = argparse.ArgumentParser(description='DB Interaction commands')
    parser.add_argument('--debug',action='store_true',help='Whether to output debug info')
    parser.add_argument('--config_file',action='store',default='db_settings.ini',help='The ini file to use for db settings. Default: %(default)s')
    subparsers = parser.add_subparsers(help='Available sub-commands')

    parser_init = subparsers.add_parser('init', help='Initiate db interaction')
    parser_init.set_defaults(func=init_wrap)
    
    parser_import = subparsers.add_parser('import', help='Import data to db from SQL file')
    parser_import.add_argument('in_file',action='store',help='SQL file to import')
    parser_import.set_defaults(func=import_wrap)

    parser_dump = subparsers.add_parser('dump', help='Dump data from db to SQL file')
    parser_dump.add_argument('out_file',action='store',help='SQL file to dump into')
    parser_dump.add_argument('--no_data',action='store_true',help='Whether to not include data in the dump')
    parser_dump.set_defaults(func=dump_wrap)

    args = parser.parse_args()
    DEBUG = args.debug
    args.func(args)
