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

import ConfigParser
from glob import glob 
import os.path
import sys

import diff_tex

# global var to hold downloaded bytes
downloaded = ''

def download(s):
    global downloaded
    downloaded += s

def ftp_directories():
    ''' Upload files to ftp, returning an error code when done
    '''
    global downloaded

    # get the settings from the ini file
    try:
        # NB: Add some error handling!
        cp = ConfigParser.SafeConfigParser()
        cp.read('ftp_settings.ini')
        
        # read the server options
        host = cp.get('Server', 'host', raw=True)
        user = cp.get('Server', 'username', raw=True)
        pw = cp.get('Server', 'password', raw=True)
        base_dir = '/%s' % cp.get('Server', 'base_dir')

        # build paths
        default_dir = '%s/%s' % (base_dir, cp.get('Destinations', 'default'))
        destinations = {}
        for opt in cp.options('Destinations'):
            if opt != 'default':
                destinations[opt] = '%s/%s' % (base_dir, cp.get('Destinations', opt))
        
    except Exception:
        raise
        print 'INI file error'
        return 1

    try:
        # create ftp connection
        import ftplib
        ftp = ftplib.FTP(host, user, pw)
    except:
        print 'Could not access FTP location' 
        return 2

    c = []
    # For each file in directory_pdfs, upload the file if it changed
    # build list of changed files
    for f in glob(os.path.normpath(os.path.join('directory_pdfs', '*.pdf'))):
        f = os.path.splitext(os.path.split(f)[1])[0]
        if diff_tex.diff_filename(f):
            c.append(f)

    os.chdir('directory_pdfs')
    for f in ['%s.pdf' % i for i in c]:
        # determine appropriate upload dir
        dest = default_dir
        for k in destinations:
            if k in f:
                # found a sepcific destination
                dest = destinations[k]
                break
        ftp.cwd(dest)

        fh = open(f, 'rb')
        #    print 'storing %s' % f
        ftp.storbinary('STOR %s' % f, fh)
        
        # download file to ensure successful upload
        ftp.retrbinary('RETR %s' % f, download)

        # compare uploaded file to downloaded one to ensure correct upload
        fh.seek(0)
        up = fh.read()
        if up != downloaded:
            print 'Uploaded file does not match downloaded file'
            return 3
        downloaded = ''
        fh.close()
        print 'Wrote %s to %s' % (f, dest)

    ftp.quit()
    if c:
        print 'All changed directory files uploaded'
    else:
        print 'No directories needed uploading'
    return 0

if __name__ == "__main__":
    sys.exit(ftp_directories())
