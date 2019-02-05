''' Build mailing lists for all the clubs, districts and MD officers in a given MD

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
import csv
import os
import os.path

import db_handler

def build_dist_club_list(dist_id):
    # obtain all clubs in the dist
    out = {}
    for c in db_handler.get_clubs_in_dist(dist_id, ['Club President', 'Club Secretary', 'Club Treasurer']):
        if c['postal']:
            out[c['name']] = c['postal']
        else:
            # no postal address given, use the postal address for officers if all are the same
            off = c['officers']
            if off and len(off) == 3 and all(off):
                if (off[0]['add'] == off[1]['add']) and (off[1]['add'] == off[2]['add']):
                    out[c['name']] = off[0]['add']
    return out
    
def make_club_lists(md=None, outdir=None):
    for d in db_handler.get_md_details(md)['dists']:
        fh = open(os.path.normpath(os.path.join(outdir, '%s_club_postal_adds.txt' % d['name'].lower().replace(' ', '_'))), 'wb')
        cl = build_dist_club_list(d['id'])
        if cl:
            keys = cl.keys()
            keys.sort()
            for k in keys:
                fh.write('%s\n%s\n\n%s\n\n\n' % (k, '-' * len(k), '\n'.join(cl[k])))
        fh.close()

def uni_convert(s):
    return ''.join([chr(ord(i)) for i in s if ord(i) < 256])

if __name__ == "__main__":
    # parse command line args, some of which may override conf settings
    import argparse
    parser = argparse.ArgumentParser(description='Build mailing lists for clubs, districts and the MD of a given MD')
    parser.add_argument('--md', action='store', default=None, 
                        help='The name of the MD to build a directory for. If not supplied, the first MD found in the database is used. ')
    parser.add_argument('--outdir', action='store', default=None, 
                        help='The directory to place the email lists into. This will be created if it does not already exist')

    args = parser.parse_args()

    if args.outdir:
        outdir = os.path.abspath(os.path.normpath(args.outdir))
        if not os.path.exists(outdir):
            os.mkdir(outdir)
    else:
        outdir = os.getcwd()

    make_club_lists(md=args.md, outdir=outdir)
    print 'Postal address lists built.'
