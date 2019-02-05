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
import db_handler
import models

from Tkinter import Tk


def copy_to_clipboard(text):
    r = Tk()
    r.withdraw()
    r.clipboard_clear()
    r.clipboard_append(text)
    r.destroy()

def print_member_details(member_id, email=None, use_prev_title=False):
    ''' Print the member details for the supplied ID
    Substitute member's email for 'email' if given
    'use_prev_title' governs whether to prepend (I)PID, (I)PCC or (I)PDG if applicable
    '''
    overrides = {}
    if email:
        overrides['email'] = email
    data = db_handler.get_member_data(member_id, overrides)

    out = []
    if data:
        # got valid data, build it
        out.append('')
        prev_title = ''
        if use_prev_title:
            prev_title = data['prev_title']
        if data['name']:
            s = 'Member: %s %s' % (data['prev_title'], data['name'])
            if data.get('deceased', False):
                s += ' (Deceased)'
            out.append(s)
        if data['partner']:
            out.append('Partner: %s %s' % ('Lion' if data['partner_lion'] else '',  data['partner']))
        if data['resigned']:
            out.append('Resigned')

        if data['join_date']:
            out.append('Joined Lions in %d' % data['join_date'])

        out.append('')
        for i in data['add']:
            out.append(i)
        out.append(data['country'])

        out.append('')
        for h,i in zip([i[0].upper() for i in db_handler.MEMBER_PHS], data['phone']):
            if i:
                out.append('%s: %s' % (h,i))

        if data['email']:
            out.append('')
            out.append('Email: %s' % data['email'])

        if data['club']:
            out.append('')
            out.append('Home Club: %s' % data['club'])
    else:
        out.append('Invalid member')
    print '\n'.join(out)
    copy_to_clipboard('\n'.join(out))

def get_officerless_clubs(struct_id, year):
    ''' Return a list of club names for clubs which do not have recorded officers
    in the given struct for the specified year
    '''
    out = []
    for c in db_handler.get_clubs_in_dist(struct_id, ['Club President', 'Club Secretary', 'Club Treasurer'], year):
        if not all(c['officers']):
            out.append(c['name'])
    return out
                      
def get_meeting_strings():
    ''' Build and return a meeting string for all clubs
    '''
    import json
    dic = {}
    meeting_model = models.Meetings.objects
    for d in db_handler.get_md_details()['dists']:
        for c in db_handler.get_clubs_in_dist(d['id'], []):
            meetings = meeting_model.filter(club__id=int(c['id']))
            s = []
            for m in meetings:
#                print meeting
                try:
                    s.append('%s %s at %s%s' % (models.weeks[m.week][1], models.weekdays[m.day-1][1], m.time.strftime('%H:%M'), 
                                                 ' (%s)' % m.spec_ins if m.spec_ins else ''))
                except:
                    print m.week, m.day, len(models.weeks), len(models.weekdays)
                    raise
            dic[int(c['id'])] = ';'.join(s)
    fh = open('meeting_strings.json','w')
    json.dump(dic, fh)
    fh.close()
    print 'done'

def write_meeting_strings():
    import json
    fh = open('altered_meetings.json', 'r')
    j = json.load(fh)
    fh.close()
    
    for k,v in j.items():
        try:
            c = models.Club.objects.get(id=int(k))
            c.meet_time = v
            c.save()
        except:
            print 'No match for club with id ', k
            raise
    print 'done'

if __name__ == "__main__":

    def member_info(args):
        print_member_details(args.member_id, use_prev_title=args.no_prev_title)

    def clubs_without_officers(args):
        print '\n'.join(get_officerless_clubs(args.id, args.year))

    # parse command line args, some of which may override conf settings
    import argparse
    parser = argparse.ArgumentParser(description='Explore MD Directory data')
    subparsers = parser.add_subparsers()

    parser_member_info = subparsers.add_parser('member_info', help='Print info for a given member ID')
    parser_member_info.add_argument('member_id', action='store', type=int, help='The member ID to look up')
    # store the flag as false so as not to need inversion when calling the print function
    parser_member_info.add_argument('--no_prev_title', action='store_false', default=True, help='Do not include title member holds through previous position (i.e. PDG, PCC, PID)')
    parser_member_info.set_defaults(func=member_info)

    parser_member_info = subparsers.add_parser('clubs_without_officers', help='Print a list of clubs without officer info for a given year and district')
    parser_member_info.add_argument('year', action='store', type=int, help='The Lionistic year to use')
    parser_member_info.add_argument('id', action='store', type=int, help='The district ID to look for clubs in')
    parser_member_info.set_defaults(func=clubs_without_officers)

    args = parser.parse_args()
    args.func(args)
