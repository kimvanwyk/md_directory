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

def build_dist_club_list(dist_id, offices=['Club President', 'Club Secretary', 'Club Treasurer'], year=None):
    if not year:
        year = db_handler.get_current_year()

    # obtain all clubs in the dist
    out = []
    for c in db_handler.get_clubs_in_dist(dist_id, offices, year):
        for n,off in enumerate(offices):
            member = c['officers'][n]
            if member and member['email']:
                out.append((c['name'], off, member['name'], member['email']))
    return out

def build_struct_off_list(struct_id, year=None):
    if not year:
        year = db_handler.get_current_year()

    # define office list
    offices = ['District Governor', 'Immediate Past District Governor', 'First Vice District Governor', 
              'Second Vice District Governor', 'Cabinet Secretary', 'Cabinet Treasurer',
               'Council Chairperson', 'Immediate Past Council Chairperson', 'Council Chairperson Elect',
               'Council Secretary', 'Council Treasurer']
    offs = []
    for o in offices:
        if 'Immediate Past' in o:
            y = year - 1
            o = o[len('Immediate Past '):]
        else:
            y = year
        offs.append((o, y))

    out = []
    for title, member in zip(offices, db_handler.get_struct_officers(offs, struct_id)):
        if member and member['email']:
            out.append((title.strip('"'), member['name'], member['email'], member['phone'][0], member['phone'][2]))

    # handle struct chairs
    for title, member in db_handler.get_struct_chairs(year, struct_id):
        if member and member['email']:
            out.append((title, member['name'], member['email'], member['phone'][0], member['phone'][2]))

    # regions and zones
    for r in db_handler.get_struct_region_details(struct_id) + db_handler.get_struct_zone_details(struct_id):
        member = r['chair']
        if member and member['email']:
            out.append(('%s Chair' % r['name'], member['name'], member['email'], member['phone'][0], member['phone'][2]))
        
    return out

def build_struct_pdgs_pccs_list(struct_id, year=None):
    if not year:
        year = db_handler.get_current_year() - 1

    # define office list
    offices = ['District Governor', 'Council Chairperson']

    out = []
    for o in offices:
        for member in (i[2] for i in db_handler.get_past_struct_officers(o, struct_id, year=year)):
            if member and member['email']:
                out.append((member['name'], member['email']))
    return out
    
def make_club_lists(md=None, year=None, outdir=None):
    if not year:
        year = db_handler.get_current_year()

    for d in db_handler.get_struct_details(db_handler.get_md(md).id)['children']:
        fh = open(os.path.normpath(os.path.join(outdir, 'club_email_adds_%s_%d.csv' % (d['name'].lower().replace(' ', '_'), year))), 'wb')
        csvfile = csv.writer(fh)
        csvfile.writerow(['Club Name', 'Office', 'Officer Name', 'Email'])
        for c in build_dist_club_list(d['id'], year=year):
            csvfile.writerow([uni_convert(i) for i in c])
        fh.close()

def uni_convert(s):
    return ''.join([chr(ord(i)) for i in s if ord(i) < 256])

def make_struct_lists(md=None, year=None, outdir=None):
    if not year:
        year = db_handler.get_current_year()

    md = db_handler.get_struct_details(db_handler.get_md(md).id)
    for d in [md['struct']] + md['children']:
        fh = open(os.path.normpath(os.path.join(outdir, '%s_email_adds_%d.csv' % (d['name'].lower().replace(' ', '_'), year))), 'wb')
        csvfile = csv.writer(fh)
        csvfile.writerow(['Office', 'Officer Name', 'Email', 'Home Phone', 'Cell Phone'])
        for c in build_struct_off_list(d['id'], year=year):
            csvfile.writerow([uni_convert(i) for i in c])
        fh.close()

def make_pdg_pcc_lists(md=None, year=None, outdir=None):
    md = db_handler.get_struct_details(db_handler.get_md(md).id)
    for title,d in [('pcc', md['struct'])] + zip(['pdg'] * len(md['children']), md['children']):
        fh = open(os.path.normpath(os.path.join(outdir, '%s_%s_email_adds.csv' % (d['name'].lower().replace(' ', '_'), title))), 'wb')
        csvfile = csv.writer(fh)
        csvfile.writerow(['Name', 'Email'])
        for c in build_struct_pdgs_pccs_list(d['id'], year=year):
            csvfile.writerow([uni_convert(i) for i in c])
        fh.close()

def make_lists(md=None, year=None, outdir=None):
    make_struct_lists(md=md, year=year, outdir=outdir)
    make_club_lists(md=md, year=year, outdir=outdir)
#    make_pdg_pcc_lists(md=md, year=year, outdir=outdir)

if __name__ == "__main__":
    # parse command line args, some of which may override conf settings
    import argparse
    parser = argparse.ArgumentParser(description='Build mailing lists for clubs, districts and the MD of a given MD')
    parser.add_argument('--md', action='store', default=None, 
                        help='The name of the MD to build a directory for. If not supplied, the first MD found in the database is used. ')
    parser.add_argument('--year', action='store', type=int, default=db_handler.get_current_year(), 
                        help='The Lionistic year to build email lists for. Defaults to the current year')    
    parser.add_argument('--outdir', action='store', default=os.getcwd(),
                        help='The directory to place the email lists into. This will be created if it does not already exist')

    args = parser.parse_args()

    if args.outdir:
        outdir = os.path.abspath(os.path.normpath(args.outdir))
        if not os.path.exists(outdir):
            os.mkdir(outdir)
    else:
        outdir = os.getcwd()

    make_lists(md=args.md, year=args.year, outdir=outdir)
#    make_club_lists(md=None, year=args.year, outdir=args.outdir)
    print 'Mailing lists built.'
