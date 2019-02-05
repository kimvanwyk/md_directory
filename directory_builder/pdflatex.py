''' 
A module to build pdf's from tex files

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
def run_shell_command(command, logging=None, timeout=30, debug=False):
    '''Execute 'command' in the shell, where 'command' is a list of command-line words
    'logging' is a file name to write the oautput to. If None, stdout is used
    'timeout' is the number of seconds to wait before timing out
    'debug' determines whether to print debug output

    returns True if command succeeds, False otherwise
    '''
    from subprocess import Popen, PIPE
    from time import sleep

    # set up logging file name
    if not logging:
        log = PIPE
    else:
        log = open(logging, 'a')
    p = Popen(command, shell=False, stdin = PIPE, stdout=log)
    if logging:
        log.close()
    # allow timeout secs for building
    result = False
    for i in range(timeout):
        if p.poll() == None:
            sleep(1)
        else:
            result = True
            break
    del p
    return result

def build_pdf(fn, outdir='directory_pdfs', logging=None, debug=False):
    ''' Build a pdf from the supplied file name, a tex file without extension
    Place the output into 'outdir'
    'logging' is a file name to write the oautput to. If None, stdout is used
    'debug' determines whether to print debug output
    Return False on failure, True otherwise
    '''
    from os.path import exists, split
    from os import mkdir, chdir, remove, getcwd
    from shutil import copy
    # create output dir if needed
    if not exists(outdir):
        mkdir(outdir)
    # if the fn is in a dir, change to it
    olddir = getcwd()
    d, fn = split(fn)
    if d:
        chdir(d)
    # attempt to remove old versions of fn.aux and fn.pdf. Ignore errors
    for e in ['aux', 'pdf']:
        try:
            remove('%s.%s' % (fn,e))
        except:
            if debug:
                print 'could not remove %s.%s ' % (fn,e)
            pass
    # set up and execute pdflatex command
    command = ['pdflatex','-interaction','errorstopmode','%s.tex' % fn]
    if debug:
        print 'Building PDF for %s.tex' % fn
    # run a 2 pass build
    for i in range(3):
        result = run_shell_command(command, logging, 30, debug)
        if not result:
            break
    # all build runs passed, present the result
    if result:
        # pdflatex complete - if the file has been made, place into outdir
        if exists ('%s.pdf' % fn):
            copy('%s.pdf' % fn, outdir)
            if debug:
                print 'done with %s' % fn
            res = True
        else:
            # return an error, no file was created
            if debug:
                print 'no pdf made for %s' % fn
            res = False
    else:
        # building failed
        if debug:
            print 'Stopped at %s' % fn
        res = False
    chdir(olddir)
    return res

def make_pdfs(files, pdf_dir = 'directory_pdfs', logging=None, debug=False):
    ''' Build a pdf out of each file in 'files', placing each pdf into 'pdf_dir'
    Return Boolean result depending on whether all files were built or not
    'logging' is a file name to append output logs to. If None, use stdout
    'debug' determines whether to print debug output
    '''

    for f in files:
        result = build_pdf(f, pdf_dir, logging, debug)
        if not result:
            if debug:
                print "Errors in building pdf's. Stopped at %s" % f
            break
    if result:
        if debug:
            print "All PDF's built and placed into %s" % pdf_dir
    return result

