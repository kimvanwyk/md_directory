'''
diff an md directory tex file with its original, ignoring the "compiled on ..." line, returning True if they differ, False otherwise

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

def junk_line(string):
    ''' Return True if the line is ignorable, False otherwise
    Ignores "compiled on..." lines
    '''
    ig = 'compiled on '
    return ig in string

def diff_strs(orig, new, print_diff=False):
    ''' Diff 2 .tex string lists, ignoring junk lines
    Return True if they differ, False otherwise
    Print full diff if 'print_diff' is true
    '''
    from difflib import context_diff
    # ignore lines that match junk_line, don't start with -+! or have a *** or --- at the top
    res = [i for i in context_diff(orig, new, n=0) 
           if not ((junk_line(i)) or (i and i[0] not in '!-+') or (len(i) > 3 and i[:3] in ['***', '---']))]
    if print_diff and res:
        print ''.join(res)
    return bool(res)

def diff_files(orig, new, print_diff=False):
    ''' Diff 2 .tex files, ignoring junk lines
    Print full diff if 'print_diff' is true
    Return True if they differ, False otherwise
    return None on error
    '''
    try:
        fo = open(orig, 'r')
        fn = open(new, 'r')
        res = diff_strs(fo.readlines(), fn.readlines(), print_diff)
        fo.close()
        fn.close()
        return res
    except:
        return None

def diff_filename(fn, print_diff=False):
    ''' Diff supplied file name 'fn', supplied with .tex extension against fn_orig.tex
    Print full diff if 'print_diff' is true
    Return True if they differ, False otherwise
    return None on error
    '''
    from os.path import exists
    return (not exists('%s_orig.tex' % fn)) or diff_files('%s_orig.tex' % fn, '%s.tex' % fn, print_diff)

if __name__ == '__main__':
    import argparse
    # Parse command line args for required files
    parser = argparse.ArgumentParser(description='Diff 2 MD Directory .tex files')
    parser.add_argument('orig',help='Original .tex file')
    parser.add_argument('new',help='New .tex file')
    parser.add_argument('--debug',action='store_true',default=False,help='Whether to output debug')
    parser.add_argument('--print_diff',action='store_true',default=False,help='Whether to output the full diff')
    args = parser.parse_args()

    res = diff_files(args.orig, args.new, args.print_diff)
    # match error code and output print to return value
    ret = {None: ('An error occured diffing %s with %s', 1),
           False: ('%s and %s match', -1),
           True: ('%s and %s differ', 0)}
    p, c = ret[res]
    if args.debug:
        print p % (args.orig, args.new)
    import sys
    sys.exit(c)
        
