#!/usr/bin/python

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

# Whether to time the directory building
TIME_RUN = True

from sqlalchemy import create_engine, Table, MetaData, and_, or_, select

from collections import defaultdict

# Add ORM location to the Python path
# This is a hideous hack, but hopefully only temporary
import sys
import os.path
import os
import shutil
sys.path.append(os.path.abspath('../'))
import common_modules.db_handler as db_handler

if TIME_RUN:
    from time import clock

CHILD_NAMES = {1: 'Branch', 2: 'Lioness', 3: 'Leos', 4: 'Lion Ladies'}
WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
MONTHS = ['', 'July', 'August', 'September', 'October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June']
member_cache = {}

def sanitize(string):
    ''' Escape Latex specific and unicode chars in the string 
    '''
    # escape troublesome Latex chars
    chars = ['_', '&', '#']
    for c in chars:
        string = string.replace(c, '\\%s' % c)
    
    # replace unicode chars with a unicode function
    chars = [c for c in string]
    for n,c in enumerate(chars):
        if ord(c) > 126:
            chars[n] = '\unichar{%d}' % ord(c)
    return ''.join(chars)

# define sanitize as a conveniently short-named function
S = sanitize

def identity(s):
    ''' identity function, which returns input
    Can be used in areas which expect a func to apply input to where no changes to the input are needed
    '''
    return s

def markup_email(email):
    ''' Return an email string, wrapped in an href
    '''
    s = email.strip()
    return (r'{\%s \href{mailto:%s}{%s}}' % ('normalsize' if len(s) < 36 else 'small', s,s))

def markup_url(url):
    ''' Return a URL string, wrapped in an href
    '''
    s = S(url)
    return S(r'\href{%s}{\burl{%s}}' % (s,s))

class Member(object):
    ''' Class to represent all member details, including homeclub.
    Normally instatiated from a RowProxy object from a query '''
    def __init__(self, mem):
        self.first_name = S(mem.first_name)
        self.last_name = S(mem.last_name)
        self.partner = S(mem.partner)
        self.partner_lion_b = mem.partner_lion_b
        self.join_date = mem.join_date
        self.home_ph = S(mem.home_ph)
        self.bus_ph = S(mem.bus_ph)
        self.email = S(mem.email)
        self.deceased_b = mem.deceased_b
        self.resigned_b = mem.resigned_b
        self.club_id = mem.club_id
        self.fax = S(mem.fax)
        self.cell_ph = S(mem.cell_ph)
        club = db.tables['md_directory_club']
        # If a club_id is available, add the club name to the object
        if getattr(mem, 'club_id', False):
            c = db.conn.execute(select([club.c.name], club.c.id == mem.club_id)).fetchone()
            if c:
                self.club = c[0]
            else:
                self.club = ''                
        else:
            self.club = ''

def make_member_col(member, pad_with_blanks=False):
    ''' Generate a list of lines of member data to go into a table. Expects a Member object
    Optional parameter pad_with_blanks specifies whether to insert extra blank spaces,
    for use in tables of more than one member, so addresses, phone numbers and emails line up.
    If member object is None, return a suitable length list of blank lines
'''
    phs = ['home_ph', 'bus_ph', 'cell_ph', 'fax']

    if member == None:
        if not pad_with_blanks:
            return []
        else:
            # Add blanks for all ph's, email, club, name
            return [''] * (len(phs) + 3)

    col = []
    # Concat first name and last name and partner name in brackets, if there is one
    col.append('%s %s' % (member.first_name, member.last_name))
    if member.partner:
        col[-1] += (' (%s)' % member.partner.strip())
    # add indicator for deceased member
    if member.deceased_b:
        col[-1] += r'\footnotemark[2]'
        if pad_with_blanks:
            # Add blanks for add's, all ph's, email, club, po_code
            col.extend([''] * (3 + len(phs)))
        return col

    # check if member resigned. If so, indicate this and return
    if member.resigned_b:
        col.append('Resigned')
        # pad the other columns if needed
        if pad_with_blanks:
            # Add blanks for all but one ph, email, club
            col.extend([''] * (1 + len(phs)))
        return col

    for p in phs:
        num = getattr(member, p)
        if num:
            # Append a phone number, using the first initial of its attr name as a label
            col.append('\\textbf{%s}: %s' % (p[:1].upper(), num))
        elif pad_with_blanks:
            # Add a blank as no num was used
            col.append('')

    if member.email:
        col.append(r'%s' % markup_email(member.email))
    elif pad_with_blanks:
        col.append('')

    if member.club:
        col.append(r'Home Club: %s' % (member.club))
    elif pad_with_blanks:
        col.append('')

    return col

def make_member_col_db_handler(member_dict, pad_with_blanks=False):
    ''' Generate a list of lines of member data to go into a table. Expects a member dict
    Optional parameter pad_with_blanks specifies whether to insert extra blank spaces,
    for use in tables of more than one member, so addresses, phone numbers and emails line up.
    If member object is None, return a suitable length list of blank lines
'''
    if member_dict == None:
        if not pad_with_blanks:
            return []
        else:
            # Add blanks for all ph's, email, country, club, po_code, name
            return [''] * (len(db_handler.MEMBER_PHS) + 5)

    col = []
    # Concat first name and last name and partner name in brackets, if there is one
    col.append(S(member_dict['name']))
    if member_dict['partner']:
        col[-1] += (S(' (%s)' % member_dict['partner']))
    # add indicator for deceased member
    if member_dict['deceased']:
        col[-1] += r'\footnotemark[2]'
        if pad_with_blanks:
            # Add blanks for all ph's, email, club
            col.extend([''] * (2 + len(db_handler.MEMBER_PHS)))
        return col

    # check if member resigned. If so, indicate this and return
    if member_dict['resigned']:
        col.append('Resigned')
        # pad the other columns if needed
        if pad_with_blanks:
            # Add blanks for all but one ph, email, club
            col.extend([''] * (1 + len(db_handler.MEMBER_PHS)))
        return col

    for n,p in zip(db_handler.MEMBER_PHS, member_dict['phone']):
        if p:
            # Append a phone number, using the first initial of its attr name as a label
            col.append('\\textbf{%s}: %s' % (n[:1].upper(), S(p)))
        elif pad_with_blanks:
            # Add a blank as no num was used
            col.append('')

    if member_dict['email']:
        col.append(r'%s' % markup_email(S(member_dict['email'])))
    elif pad_with_blanks:
        col.append('')

    if member_dict['club']:
        col.append(r'Home Club: %s' % (S(member_dict['club'])))
    elif pad_with_blanks:
        col.append('')

    return col

def make_latex_table(col_list, col_styles=None, header=None):
    ''' Build a latex table, with column rows drawn from the lists in 'col_list'
    optional 'col_styles' specifies Latex column styles - 'l', 'X' etc
    optional 'header' prepends a header row and horizontal line
    '''
    # Find which is the longest passed in list, and pad all others with blank lines to the same length
    # find length of longest list
    long = max([len(l) for l in col_list])
    for l in col_list:
        if long > len(l):
            l.extend(['']*(long-len(l)))
    # if no col_styles, assume "l" for each entry in the table
    if not col_styles:
        col_styles = ['l' for i in range(len(col_list))]
    
    col_styles = ' '.join(col_styles)
    # Work out whether doing tabularx or tabular tables
    table = 'tabular'
    opts = '[t]'
    ret = []
    if 'X' in col_styles:
        table += 'x'
        opts = r'{\textwidth}[t]'
    # Return a latex table, with each row having elements from each list in col_lists
#   TODO: if len(col_list) > 1:
    if 1:
        ret.append(r'\begin{%s}%s{%s}' % (table, opts, col_styles))
    # If header is set, use it with a vertical line underneath before filling in table rows
    if header:
        ret.append(r' & '.join(header) + r'\\')
        ret.append(r'\hline')
    # append each row to the table
    # the reduce ensures there is at least one entry in the line
    ret.append('\\\\\n'.join(map(' & '.join, [i for i in zip(*col_list) if any(i)])) + r'\\')
#   TODO: if len(col_list) > 1:
    if 1:
        ret.append('')
        ret.append(r'\end{%s}' % table)
        ret.append(r'\\')
    return ret

class LatexHeaderException(Exception):
    pass

class LatexHeader(object):
    ''' A class to hold a method to create a set of Latex document headers.
    Created as an object to allow the authors of the directory to be set once only
    '''
    authors = None

    def make_latex_header(self, inlist, title, type):
        ''' Return an appropriate set of Latex document options
        'inlist ' is a set of lines to prepend the header lines to
        'title' is the title of the directory
        'type' is a Latex doc type, either "article" or "report"
        'authors' is a list of people to contact about the directory, of form (name, title, email)
        '''
        lines = []
        lines.append(r'\documentclass[a4paper]{%s}' % type)
        # UTF8 support for special chars
        lines.append(r'\usepackage[utf8x]{inputenc}')
        lines.append(r'\usepackage[T1]{fontenc}')
        lines.append(r'\usepackage{textcomp}')
        lines.append(r'\usepackage{lmodern}')

        lines.append(r'\usepackage{tabularx}')
        lines.append(r'\usepackage{array}')
        lines.append(r'\usepackage{multicol}')
        lines.append(r'\usepackage{hyperref}')
        lines.append(r'\usepackage{url}')
        lines.append(r'\usepackage{breakurl}')
        lines.append(r'\usepackage{graphicx}')
        # support for symbols and better footnote handling
        lines.append(r'\usepackage[bottom, symbol*]{footmisc}')
        # lines.append(r'\usepackage{times}')    
        lines.append(r'\usepackage[margin=2cm,ignoreheadfoot]{geometry}')
        lines.append(r'\hypersetup{colorlinks={true}, urlcolor=blue, linkcolor=black}')
        lines.append(r'\urlstyle{same}')
        lines.append(r'\usepackage{titlesec}')
        lines.append(r'\titleformat{\chapter}{\Large\bfseries}{}{0pt}{\huge}')
        lines.append(r'\usepackage{savetrees}')

        lines.append(r'\begin{document}')
        import datetime
        d = datetime.datetime.now()
        # Build a cover page
        lines.append(r'\begin{titlepage}')
        lines.append(r'\begin{center}')
        lines.append(r'\includegraphics{lionsemblem_clr.png}\\')
        lines.append(r'\Huge')
        lines.append(r'%s\\' % title)
        lines.append(r'\normalsize')
        # e.g. "Monday 29 Nov 2010 at 15:44"
        lines.append(r'compiled on %s\\' % d.strftime("%A %d %b %Y at %H:%M"))
        lines.append(r'\end{center}')
        lines.append(r'')
        lines.append(r'')
        # add list of people to contact for directory changes
        lines.append(r'For additions or corrections to this directory, contact:\\')
        lines.append(r'\begin{itemize}')    
        if self.authors:
            for name, title, email in self.authors:
                lines.append(r'\item %s, %s, %s' % (name, title, markup_email(email)))
        lines.append(r'\end{itemize}')    
        lines.append(r'\end{titlepage}')
        lines.append(r'\tableofcontents{}')
        lines.append(r'\newpage')
        lines.extend(inlist)
        return lines

def get_member(member_id, email=None, home_ph=None, fax=None):
    '''obtain a Member object from the member_id passed in
    Append the supplied email if one is supplied
    TODO: Error checking?
    I the member_id is None, return None
    '''
    if member_id == None:
        return member_id
    member_t = db.tables['md_directory_member']
    m = Member(db.conn.execute(select([member_t], member_t.c.id == member_id)).fetchone())
    l = locals()
    if email:
        m.email = email
    if home_ph:
        m.home_ph = S(home_ph)
    if fax:
        m.fax = S(fax)
    return m

def get_title(off_id):
    ''' Return office id (the supplied value), office title and immediate past flag from office id
    '''
    t = db.tables['md_directory_officertitle']
    title = db.conn.execute(select([t.c.title, t.c.ip_id], t.c.id == off_id)).fetchone()
    ip = False
    if title[1]:
        # if this is an immediate past position, return the id of the item it points to
        off_id = title[1]
        ip = True
    return (off_id, title[0], ip)
    
def get_past_officer_latex(office, deceased, offs, in_district, prev_district=False):
    ''' Generate the latex for a list of past officers in 'offs' for the office title of 'office'.
    'in_district' governs whether to add a title text that these are officers from outside the district

    Returns (text, deceased flag)
    '''
    ret = []
    # check if office spans 2 years:
    if office in ['International Director']:
        num_years = 2
    else:
        num_years = 1

    if offs:
        # beg tracks the starting month of the term in office, only useful if one person didn't serve the whole term
        beg = 1
    # Return a list of (year served, end month, member dict)

    for y, month, member_dict,struct_name in offs:
        if member_dict:
            if member_dict['deceased']:
                deceased = True
            # establish first column of member table. If in_district, add the district the officer served in
            # If not a full term, add the months it spanned
            col = [r'\textbf{%d/%d}' % (y, y+num_years), 
                   '%s' % (((month < 12) or (beg > 1)) and '(%s to %s)' 
                           % (MONTHS[beg][:3], MONTHS[month][:3]) or '')]
            # add member to table.
            mc = make_member_col_db_handler(member_dict)
            if in_district or prev_district:
                mc.extend(['\\textbf{Served in %s}' % struct_name])
            ret.extend(make_latex_table([col, mc]))
            if  month < 12:
                beg = month + 1
            else:
                beg = 1
    return (deceased, ret)

def get_past_officers(office, struct_id, other_districts, footnote=False, prev_structs=False):
    ''' Return a tuple of (.tex list of details of past officers, Bool of whether the called to higher service footnote has been printed)
    The .tex list is based on 'office', the name of the office from the office titles table,
    for the given struct id
    'footnote' governs whether the footnote has already been printed
    'other_districts' governs whether to include a list of officers from other districts
    '''
    ret = []
    ret.append('')
    ret.append(r'\setlength{\columnseprule}{2pt}')
    ret.append(r'\begin{multicols}{2}[\section{Past %ss}]' % office)

    offs = db_handler.get_past_struct_officers(office, struct_id, other_structs=other_districts, prev_structs=prev_structs, year=cur_year)
    deceased = False
    if prev_structs and offs['prev']:
        deceased, text = get_past_officer_latex(office, deceased, offs['prev'], in_district=False, prev_district=True)
        ret.extend(text)
    deceased, text = get_past_officer_latex(office, deceased, offs['local'], in_district=False, prev_district=False)
    ret.extend(text)

    if other_districts and offs['other']:
        ret.append(r'\section{Past %ss from other Districts}' % office)
        deceased, text = get_past_officer_latex(office, deceased, offs['other'], in_district=True, prev_district=False)
        ret.extend(text)

    if ret:
        # ret has some content, must close multicols
        ret.append(r'\end{multicols}')

    if deceased and not footnote:
        # insert footnote if there isn't already one
        ret.append(r'\footnotetext[2]{Called to higher service}')
        footnote = True
    return (ret, footnote)

def get_officers(offices, struct_id):
    ''' Return a list of .tex  lines holding tables of struct officers, from the list of (office id, use_child) in 'offices'
    'use_child', if true, looks up all the off id's in the children of the struct instead of using the struct itself
    
    '''
    ret = []
    offs = []
    t = db.tables['md_directory_struct']
    for o,use_child in offices:
        if use_child:
            children = db.conn.execute(select([t.c.id, t.c.name], 
                                              and_(t.c.parent_id == struct_id,
                                                   t.c.in_use_b == 1))).fetchall()
            for c in children:
                offs.append((o, c[0], ', District %s' % c[1]))
        else:
            offs.append((o,struct_id, ''))

    for o,i,text in offs:
        o, title, ip = get_title(o)
        year = cur_year
        # for ip, look up details of office holder from previous year
        if ip:
            year = cur_year - 1
        t = db.tables['md_directory_structofficer']
        sel = select([t], and_(t.c.year == year, t.c.struct_id == i, t.c.office_id == o))
        officer = db.conn.execute(sel).fetchone()
        if officer:
            # officer acquired, create a latex table
            m = get_member(officer.member_id, officer.email)
            if m and not m.deceased_b and not m.resigned_b: 
                ret.append('')
                ret.append(r'\subsection{%s%s}' % (title, text))
                ret.extend(make_latex_table([make_member_col(m)]))
    return ret

def get_officers_db_handler(offices, struct_id):
    ''' Return a list of .tex  lines holding tables of struct officers, from the list of (office id, use_child) in 'offices'
    'use_child', if true, looks up all the off id's in the children of the struct instead of using the struct itself
    
    '''
    ret = []
    offs = []
    for o,use_child in offices:
        if use_child:
            # get child struct ids for struct
            children = db.conn.execute(select([t.c.id, t.c.name], t.c.parent_id == struct_id)).fetchall()
            for c in children:
                offs.append((o, c[0], ', District %s' % c[1]))
        else:
            offs.append((o,struct_id, ''))

    for o,i,text in offs:
        o, title, ip = get_title(o)
        year = cur_year
        # for ip, look up details of office holder from previous year
        if ip:
            year = cur_year - 1
        t = db.tables['md_directory_structofficer']
        sel = select([t], and_(t.c.year == year, t.c.struct_id == i, t.c.office_id == o))
        officer = db.conn.execute(sel).fetchone()
        if officer:
            # officer acquired, create a latex table
            m = get_member(officer.member_id, officer.email)
            if m and not m.deceased_b and not m.resigned_b: 
                ret.append('')
                ret.append(r'\subsection{%s%s}' % (title, text))
                ret.extend(make_latex_table([make_member_col(m)]))
    return ret

def get_chairs(struct_id):
    ''' Return a list of .tex lines holding all chairs for the given struc,tm alphabetically
    '''
    ret = []
    t = db.tables['md_directory_structchair']
    sel = select([t], and_(t.c.struct_id == struct_id, t.c.year == cur_year), order_by=t.c.office.asc())
    chairs = db.conn.execute(sel)
    for chair in chairs:
        m = get_member(chair.member_id, chair.email)
        if m and not m.deceased_b and not m.resigned_b:
            ret.append('')
            ret.append(r'\subsection{%s}' % S(chair.office))
            cols = [make_member_col(m)]
            if chair.committee_members:
                cols[0].extend(['\n', r'\textbf{Committee Members:}'])
                cols[0].extend([i.strip() for i in sanitize(chair.committee_members).split(',')])
            ret.extend(make_latex_table(cols))
    return ret

def get_chap_heading(struct, title):
    ''' create a chapter heading for the overall document
    takes in the struct RowProxy object and a title (i.e. Multiple District), to use in referring to the current structure
    '''
    name = struct['name']
    # chap is a string, used for chapter totals, for the overall document
    return r'\chapter{%s}' % name

def get_merch_centre(md_id):
    ''' Return .tex content with details of a Merchandise Centre for a given MD id
    '''
    ret = []
    mcs = db_handler.get_merch_centres(md_id)
    for mc in mcs:
        # merch centre found, create .tex output
        ret.append(r'\section{Merchandise Centre}')
        if mc['manager']:
            ret.append(r'\subsection{Manager}')
            ret.extend(make_latex_table([make_member_col_db_handler(mc['manager'])]))
        if mc['fin_advisor']:
            ret.append(r'\subsection{Financial Advisor}')
            ret.extend(make_latex_table([make_member_col_db_handler(mc['fin_advisor'])]))
    
        ret.append(r'\subsection{Sales and Administration Contact Details}')
        ret.append(r'\begin{tabular}[t]{l l}')        
        # for each of the entries in a list of (attr, title, f), if a key in mc, add a .tex table entry with title in the first col,
        # and value in the second, passed through f
        entries = [('contact_person', 'Contact Person', S),
                   ('add1', 'Address', S)] + [('add%d' % i, '', S) for i in range(2,6)] + [('po_code', '', identity),
                                                                                           ('tel', 'Telephone', S),
                                                                                           ('fax', 'Fax', S),
                                                                                           ('email', 'Email', markup_email),
                                                                                           ('website', 'Website', markup_url)]
        for key, title, f in entries:
            if mc[key]:
                ret.append(r'%s & %s\\' % (title, f(mc[key])))
        ret.append(r'\end{tabular}')       
    return ret

def get_brightsight_offices(md_id):
    ''' Return .tex content with details of a Merchandise Centre for a given MD id
    '''
    ret = []
    offs = db_handler.get_brightsight_offices(md_id)
    ret.append(r'\section{Lions Operation Brightsight Office}')
    for off in offs:
        ret.append(r'\subsection{Contact Details}')
        ret.append(r'\begin{tabular}[t]{l l}')        
        # for each of the entries in a list of (attr, title, f), if a key in mc, add a .tex table entry with title in the first col,
        # and value in the second, passed through f
        entries = [('contact_person', 'Contact Person', S),
                   ('add1', 'Physical Address', S)] + [('add%d' % i, '', S) for i in range(2,6)]
        entries += [('postal1', 'Postal Address', S)] + [('postal%d' % i, '', S) for i in range(2,6)] + [('po_code', '', identity),
                                                                                                         ('tel', 'Telephone', S),
                                                                                                         ('fax', 'Fax', S),
                                                                                                         ('email', 'Email', markup_email),
                                                                                                         ('website', 'Website', markup_url)]
        for key, title, f in entries:
            if off[key]:
                ret.append(r'%s & %s\\' % (title, f(off[key])))
        ret.append(r'\end{tabular}')       

        ret.append(r'\subsection{Manager Details}')
        ret.append(r'\begin{tabular}[t]{l l}')        
        # for each of the entries in a list of (attr, title, f), if a key in mc, add a .tex table entry with title in the first col,
        # and value in the second, passed through f
        entries = [('manager', 'Manager', S),
                   ('manager_cell_ph', 'Cell Phone', S),
                   ('manager_email', 'Email', markup_email)]
        for key, title, f in entries:
            if off[key]:
                ret.append(r'%s & %s\\' % (title, f(off[key])))
        ret.append(r'\end{tabular}')       

    return ret

def get_dist_office(dist_id):
    ''' Obtain and return a .tex list of the district office for the given district id
    '''
    ret = []
    t = db.tables['md_directory_districtoffice']
    office = t.select(t.c.struct_id == dist_id).execute().fetchone()
    if office:
        # district office found, add its details below
        ret.append(r'\section{District Office}')
        ret.append(r'\begin{tabular}[t]{l l}')        
        # for each of the entries in a list of (attr, title, f), if office.attr, add a .tex table entry with title in the first col,
        # and office.attr in the second, passed through f
        entries = [('contact_person', 'Contact Person', S),
                   ('hours', 'Operating Hours', S),
                   ('add1', 'Physical Address', S)] + \
                   [('add%d' % i, '', S) for i in range(2,6)] + \
                   [('postal1', 'Postal Address', S)] + \
                   [('postal%d' % i, '', S) for i in range(2,6)] + \
                   [('po_code', '', identity),
                   ('tel', 'Telephone', S),
                   ('fax', 'Fax', S),
                   ('email', 'Email', markup_email),
                   ('website', 'Website', markup_url)]
        for attr, title, f in entries:
            if getattr(office, attr):
                ret.append(r'%s & %s\\' % (title, f(getattr(office, attr))))
        ret.append(r'\end{tabular}')       
    return ret

def get_merls(dist_id):
    ''' Obtain a return a .tex list of the MERL coordinators for a given district
    '''
    t = db.tables['md_directory_merlcoordinators']
    ret = []
    merls = t.select(and_(t.c.struct_id == dist_id, t.c.year == cur_year)).execute().fetchall()
    if merls:
        # MERL coords found, create a 2 column list of them 
        ret.append(r'\setlength{\columnseprule}{2pt}')
        ret.append(r'\begin{multicols}{2}[\section{M.E.R.L Coordinators}]')
    for merl in merls:
        m = get_member(merl.member_id)
        if m: 
            ret.extend(make_latex_table([make_member_col(m)]))
            ret.append(r'\\')
    if merls:
        ret.append(r'\end{multicols}')
    return ret

def get_regions_and_zones(struct_id):
    ''' Build lists of region details and zone details for the supplied struct_id
    '''
    # set up a default dict to hold a blank list on first use
    regions_dict = defaultdict(list)
    zones_dict = defaultdict(list)
    out = []

    # build a dict, keyed by region id with a list of zone names in that region as the value, by looping over each zone:
    t = db.tables['md_directory_zone'].c    
    items = db.conn.execute(select([t.region_id, t.name],
                                   and_(t.struct_id == struct_id, t.in_region_b == True)).order_by(t.name)).fetchall()

    for r, name in items:
        regions_dict[r].append(name)

    # Get region name and chair member id for each region, ordered by region name
    t = db.tables['md_directory_region']
    t2 = db.tables['md_directory_regionchair']
    regions = db.conn.execute(select([t.c.name, t.c.id],
                                   and_(t.c.struct_id == struct_id)).order_by(t.c.name)).fetchall()
    ordered = []
    # generate an ordered list of tuples, ordered by region name
    for r in regions:
        # obtain chair, if there is one
        chair = db.conn.execute(select([t2.c.member_id, t2.c.email],
                                   and_(t2.c.year == cur_year, r[1] == t2.c.parent_id))).fetchone()
        if chair:
            (chair,email) = chair
        else:
            chair,email = (None,None)
        # strip "Region " from beginning of name to aid sorting
        ordered.append((r.name[7:],(r[0], chair, email, r[1])))
    ordered.sort()

    for k,r in ordered:
        # ignore k, was only used for ordering
        out.append('')
        # sort zone names for this region, comparing on whatever comes after "zone "
        names = regions_dict[r[3]]
        names.sort(cmp=lambda x,y: cmp(int(x[5:]), int(y[5:])))
        # Add zones and chairperson to a latex table
        out.append(r'\subsection{%s}' % (r[0]))
        header = [r'\textbf{Zones}', r'\textbf{Chairperson}']
        out.extend(make_latex_table([names, make_member_col(get_member(r[1], r[2]),False)], ['X', '|', 'X'], header))

    ret = []
    # Regions handled, if there were any. Output the region listings.
    if regions:
        ret.append('')
        ret.append(r'\section{Regions}')
        ret.extend(out)

    # reset out, to hold zones
    out = []
    # build a dict, keyed by zone with a list of club names in that zone as the value, by looping over each club:
    t = db.tables['md_directory_club']
    clubs = list(db.conn.execute(select([t.c.id, t.c.name, t.c.type, t.c.zone_id],
                                   and_(t.c.struct_id == struct_id, t.c.closed_b == False))).fetchall())
    for (cid, name, ctype, zid) in clubs:
        tc = db.tables['md_directory_clubzone']
        tz = db.tables['md_directory_zone']
        res = db.conn.execute(select([tc.c.zone_id], and_(tc.c.club_id == cid, tc.c.year == cur_year,
                                                          tz.c.id == tc.c.zone_id, tz.c.struct_id == struct_id))).fetchone()
        if res:
            zone_id = res[0]
        else:
            zone_id = zid
        # add club type if not a regular club
        if ctype > 0:
            name += ' (%s Club)' % CHILD_NAMES[ctype]
        zones_dict[zone_id].append(name)

    # Get zone name chair member_id for each zone, ordered by zone name
    t = db.tables['md_directory_zone'].c
    t2 = db.tables['md_directory_zonechair'].c
    zones = db.conn.execute(select([t.name, t.id],
                                   and_(t.struct_id == struct_id)).order_by(t.name)).fetchall()

    # order zone names numerically
    ordered = []
    for z in zones:
        # obtain chair, if there is one
        chair = db.conn.execute(select([t2.member_id, t2.email],
                                   and_(t2.year == cur_year, z[1] == t2.parent_id))).fetchone()
        if chair:
            (chair,email) = chair
        else:
            chair,email = (None,None)
        # strip "Zone " from beginning of name to aid sorting
        ordered.append((int(z.name[5:]),(z[0], chair, email, z[1])))
    ordered.sort()

    for k,z in ordered:
        out.append('')
        # sort club names for this zone
        names = zones_dict[z[3]]
        names.sort()
        # Add clubs and chairperson to a latex table
        out.append(r'\subsection{%s}' % (z[0]))
        header = [r'\textbf{Clubs}', r'\textbf{Chairperson}']
        out.extend(make_latex_table([names, make_member_col(get_member(z[1], z[2]),False)], ['X', '|', 'X'], header))

    # Zones handled, if there were any. Output the zone listings.
    if zones:
        ret.append('')
        ret.append(r'\section{Zones}')
        ret.extend(out)
    return ret

def get_club_info(struct_id):
    ''' Supply a list of .tex lines with the details of each club in the supplied district
    '''
    ret = []
    # grab a list of all clubs in the struct
    t = db.tables['md_directory_club']
    clubs = list(t.select(and_(t.c.struct_id == struct_id, t.c.closed_b == False)).execute())
    clubs.sort(key=lambda c: c.name)
    for c in clubs: 
        club_officers = []
        # obtain the correct title id for each club officer and see if a member_id exists for the club's officer
        for o in db.offices[c.type]:
            o, title, ip = get_title(o)
            t = db.tables['md_directory_clubofficer']   
            off = t.select(and_(t.c.club_id == c.id, t.c.year == cur_year, t.c.office_id == o)).execute().fetchone()
            # only process if an actual officer has been selected
            if off and off.member_id:
                # insert the office email for the club
                m = get_member(off.member_id, off.email, off.phone, off.fax)
                if m and not m.deceased_b and not m.resigned_b:
                    # if a member is returned, set the club to None as the club is already known in this section
                    # append to club officers to form a list of (officer title, member obect)
                    m.club = None
                    club_officers.append([r'\textbf{%s}' % title, m])
        ret.append(r'\noindent')
        ret.append(r'\begin{minipage}{\textwidth}')
        # Add club name to a subsection
        str = '%s' % S(c.name)
        # 0: 1: branch; 2: Lioness club; 3: Leos; 4: Lion Ladies
        if c.type > 0:
            # If a child club (branch, Lioness etc), add this to the title
            # Get name of parent club
            str += ' (%s Club' % CHILD_NAMES[c.type]
            table = db.tables['md_directory_club']
            parent = db.conn.execute(select([table.c.name], table.c.id == c.parent_id)).fetchone()
            if parent:
                str += ' of %s' % S(parent[0])
            str += ')'
        # add club name as a new subsect
        ret.append(r'\subsection{%s}' % str)
        chartered = ''
        if c.charter_year:
            # Set chartered text depending on club type
            ch_str = 'Chartered'
            # if not a regular club, don't use "Chartered"
            if c.type > 0:
                ch_str = 'Established'            
            chartered = '%s: %d' % (ch_str, c.charter_year)

        # Get zone and region info
        zonestr = ''
        tc = db.tables['md_directory_clubzone']
        tz = db.tables['md_directory_zone']
        zone = db.conn.execute(select([tz], and_(tc.c.zone_id == tz.c.id, tc.c.club_id == c.id, 
                                                 tc.c.year == cur_year, tz.c.struct_id == struct_id))).fetchone()
        if not zone:
            tz = db.tables['md_directory_zone']
            zone = db.conn.execute(select([tz], and_(tz.c.id == c.zone_id))).fetchone()
        if zone:
            # Check if zone is in a region
            if zone.in_region_b:
                t = db.tables['md_directory_region'].c
                # build a string of zone name, region name
                zonestr = S('%s, %s' % (db.conn.execute(select([t.name], t.id == zone.region_id)).fetchone()[0], zone.name))
            else:
                # just use zone name
                zonestr = S(zone.name)
        ret.extend(make_latex_table([[chartered], [zonestr]], ['X', 'X']))

        if c.suspended_b:
            ret.append(r'\noindent')
            ret.append(r'(Club under suspension)\\')

        if club_officers:
            # add club officers, if there were any. Use padding so they all line up
            ret.append(r'\noindent')
            cols = [r'>{\raggedright}X' for i in club_officers[:-1]] + ['X']
            ret.extend(make_latex_table([make_member_col(i[1], True) for i in club_officers], cols, [off[0] for off in club_officers]))
        else:
            ret.append(r'No club officer information available\\' )
        if c.website:
            ret.append(r'\textbf{Website}: %s\\' % markup_url(c.website))

        # look up the clubs meetings
        meetstr = [c.meet_time]
        for a in range(1,6):
            if getattr(c, 'add%d' % a):
                meetstr.append(S(getattr(c, 'add%d' % a)))
        if any(meetstr):
            ret.append('\\textbf{Meetings}: %s' % ', '.join(meetstr))
        else:
            ret.append('No meeting information available')

        postal = []
        for attr in ['postal%d' % a for a in range(1,5)] + ['po_code']:
            if getattr(c, attr):                
                postal.append(S(getattr(c, attr)))
        if postal:
            ret.append(r'\\')
            ret.append('\\textbf{Club Postal Address}: %s' % ', '.join(postal))
        # Check if there are any child clubs to list
        table = db.tables['md_directory_club']            
        children = db.conn.execute(select([table.c.name, table.c.type], and_(table.c.parent_id == c.id, table.c.type > 0, table.c.closed_b == False))).fetchall()
        child_dict = defaultdict(list)
        for ch in children:
            child_dict[ch.type].append(ch.name)
        if child_dict:
            for i in range(1,5):
                names = child_dict.get(i)
                if names:
                    ret.append(r'\\')
                    names.sort()
                    # Add child info, with a plural 
                    ret.append('\\textbf{%s Club%s}: %s' % (CHILD_NAMES[i], ['', 's'][bool(len(names) > 1)], ', '.join(S(b) for b in names)))
        ret.append(r'\\')
        ret.append(r'\end{minipage}')
        ret.append('')
    return ret

def decorate_tex_file(lines, title, fn, latex_type):
    ''' Append latex headers and closing lines to a .tex list
    Place those lines into a file, named by 'fn'
    'lines' is the .tex list to decorate
    'title' is the title to apply for the directory
    'latex_type' is the type of doc - article or report
    No return
    '''
    lines.append(r'\end{document}')
    # create and add header to file
    header = LatexHeader()
    lines = header.make_latex_header(lines, title, latex_type)
    fh = open('%s.tex' % fn, 'w')
    fh.write('\n'.join(lines))
    fh.close()

def get_chap_and_officers(struct, org_name, board_title, offices):
    ''' Return chapter and officer tex for a given struct.
    'org_name' and 'board_title' are the name of the struct and its board, eg 'District' and 'Cabinet'
    'offices' is a list of ids to get officer details for

    Return single file tex and total-only tex, both as lists
    '''
    ret = []
    ret.append(r'\setlength{\columnseprule}{2pt}')
    ret.append(r'\begin{multicols}{2}[\section{%s %s}]' % (org_name, board_title))
#    ret.append(r'\raggedright')
    ret.extend(get_officers(offices, struct['id']))
    ret.extend(get_chairs(struct['id']))
    ret.append(r'\end{multicols}')
#    Set website to the appropriate md or dist website attr
    if struct['website']:
        ret.append('\section{%s Website}' % org_name)
        ret.append(r'\textbf{Website}: %s\\' % markup_url(struct['website']))

#    ret.append(r'\flushbottom')
    return (ret, [get_chap_heading(struct, org_name)])

def build_directory_contents(struct_id, year):
    ''' Produce a list of file names, without extensions, holding .tex contents for building directories,
    for the MD details, each district and then an overall directory
    'md_name' is the name of the MD to build a directory for. If None, the first MD in the list is used
    'year' is the Lionistic year of interest
    '''
    files = []
    # out tracks the .tex lines for the current chapter - council details or district, for eg.
    out = []
    # total tracks all .tex lines for overall document, to which additional lines are added to handle several chapters in one doc. 
    total = []
    global cur_year
    cur_year = year
    # build a string to prefix files with
    year_prefix = '%d%d' % (year, year + 1)

    structs = db_handler.get_struct_details(struct_id)
    if structs:
        md = structs['struct']
        # Add chapter heading for an MD
        o, tot = get_chap_and_officers(md, 'Multiple District', 'Council', db.offices['md'])
        total.extend(tot)
        out.extend(o)
        # obtain merch center 
        out.extend(get_merch_centre(md['id']))
        out.extend(get_brightsight_offices(md['id']))
        # Add PCC info
        # council chair is officer ID 11
        # Set not to show officers from other districts
        tex, footnote = get_past_officers('Council Chairperson', md['id'], False, prev_structs=False)
        out.extend(tex)
        # Add ID info, ID 21. Pass in footnote from previous list of past officers
        # use only .tex return from get_past_officers
        # Set not to show officers from other districts
        out.extend(get_past_officers('International Director', md['id'], False, footnote, prev_structs=False)[0])
        total += out
        # build Latex .tex file, using an article style
        fn = os.path.normpath(os.path.join('build', '%s_%s_directory_md_details_only' % (year_prefix, md['name'].lower().replace(' ', '_'))))
        files.append(fn)
        decorate_tex_file(out, '%d/%d %s Directory - MD Specific Details' % (year, year + 1, md['name']), fn, 'article')

    for dist in structs['children']:
        # Add chapter heading for a district
        out = []
        name = '%s' % dist['name']
        o, tot = get_chap_and_officers(dist, 'District', 'Cabinet', db.offices['dist'])
        total.extend(tot)
        out.extend(o)
        # Add district office and LERL advisors. One or both may be blank
        out.extend(get_dist_office(dist['id']))
        out.extend(get_merls(dist['id']))
        # Add all regions and zones.
        out.extend(get_regions_and_zones(dist['id']))
        out.append('')
        out.append(r'\section{Clubs}')
        # for each club, add the club and its officers, address etc
        out.extend(get_club_info(dist['id']))

        # Add PDG info
        out.append('')
        # DG is 5
        out.extend(get_past_officers('District Governor', dist['id'], True, prev_structs=True)[0])
        total += out
        fn = os.path.normpath(os.path.join('build', '%s_%s_directory' % (year_prefix, name.lower().replace(' ', '_'))))
        files.append(fn)
        decorate_tex_file(out, '%d/%d %s Directory' % (year, year+1, name), fn, 'article')

    fn = os.path.normpath(os.path.join('build', '%s_%s_directory_full_details' % (year_prefix, md['name'].lower().replace(' ', '_'))))
    files.append(fn)
    decorate_tex_file(total, '%d/%d %s Directory' % (year, year+1, md['name']), fn, 'report')
    return files

def get_current_year():
    ''' Return the current Lionistic year
    '''
    from datetime import datetime
    now = datetime.now()
    year = now.year
    if now.month <= 6:
        year = year - 1
    return year

class DBHandler(object):
    conn = None
    tables = None
    club_offices = None
    offices = None

    def __init__(self, username, password, schema, host, port, db_type):
        engine = create_engine('%s://%s:%s@%s:%s/%s' % (db_type, username, password, host, port, schema), echo=False)
        metadata = MetaData()
        metadata.bind = engine
        self.conn = engine.connect()
        self.tables = {}
        table_list = ['md_directory_club', 'md_directory_clubofficer', 
                      'md_directory_clubzone', 'md_directory_meetings', 
                      'md_directory_member', 'md_directory_merchcentre', 'md_directory_districtoffice',
                      'md_directory_merlcoordinators', 'md_directory_officertitle', 'md_directory_region', 
                      'md_directory_regionchair', 'md_directory_struct', 'md_directory_structchair', 
                      'md_directory_structofficer', 'md_directory_zone', 'md_directory_zonechair']
        for t in table_list:
            self.tables[t] = Table(t, metadata, autoload=True, schema='%s' % schema)

        self.offices = {}
        # dg, ipdg, 1vdg, 2vdg, sec, treas
        self.offices['dist'] = [(5,False),(6,False),(7,False),(8,False),(9,False),(10,False)]
        # cc, dgs, 1vdgs, ipcc, cce, sec, treas
        self.offices['md'] = [(11,False),(5,True),(7,True),(12,False),(13,False),(14,False),(15,False)] 
        # types of club
        # 0: regular club (pres, sec, treas); 1: branch (liason, coord, vice coord); 2: Lioness club (pres, sec, treas); 
        # 3: Leos (advisor, pres, sec, treas); 4: Lion Ladies (pres)
        self.offices.update({0:[1,2,3], 1:[16,1,2], 2:[1,2,3], 3:[20,1,2,3], 4:[1]})

def delete_file(f):
    ''' Remove the specified file, ignoring errors
    '''
    try:
        from os import remove
        remove(f)
    except:
        pass

def exit(code=1):
    ''' Exit the application using supplied error code
    '''
    import sys
    sys.exit(code)

def build_directories(db_settings, authors=[], md_name=None, year=None):
    ''' Process conf settings and build all directories
    Return 0 on success, a different code otherwise

    'db_settings' is a dict of db parameters, consisting of
       'username'
       'password'
       'host'
       'schema'
       'db_type' - these values are all as expected by DBHandler
    'authors' is a list of author information tuples, holding (name, title, email) for each author
       If left empty, no author info will be added to the directory
    'md_name' is the name of the MD to look up
       If left None, the first md found in the db will be used
    'year' is the Lionistic year of interest.
       If left None, the current year will be used
    '''
    global db 
    db = DBHandler(**db_settings)
    
    # set up header with author
    LatexHeader.authors = authors
    
    if year==None:
        year = get_current_year()
    try:
        # obtain id of MD struct to use
        md = db_handler.get_md(md_name)
        if md == None:
            # name supplied, check it existed
            if md_name:
                # no record, print error and exit
                print 'Cannot find an MD named %s in the DB' % md_name
                return 4
            else:
                # no record, print error and exit
                print "Cannot find any MD's in the DB"
                return 5
    except:
        return 3

    # build PDF's
    if not os.path.exists('build'):
        os.mkdir('build')
    shutil.copy2('lionsemblem_clr.png', 'build')
    files = build_directory_contents(md.id, year)
    # go to the build directory, creating it if need be
    from pdflatex import build_pdf
    # delete logging file
    # build each PDF, but only if it has differed from the original
    from diff_tex import diff_filename
    for f in files:
        if diff_filename(f):
            delete_file('log.txt')
            print 'Building PDF of %s' % f
            if not build_pdf(f, outdir='../directory_pdfs', logging='log.txt', debug=True):
                print 'Error encountered, see %s for details' % 'log.txt'
                return 2
            else:
                print 'PDF of %s successfully built' % f 
        else:
            print '%s is unchanged, will not build PDF' % f
    print
    print "All necessary PDF's have been built"
    return 0

if __name__ == "__main__":
    if TIME_RUN:
        start_time = clock()
    # parse command line args, some of which may override conf settings
    import argparse
    parser = argparse.ArgumentParser(description='Build MD Directory')
    parser.add_argument('--md', action='store', default=None, help='The name of the MD to build a directory for. This value overrides the setting in the settings.ini file. If not supplied either on the command line or in the settings.ini file, the first MD found in the database is used. ')
    parser.add_argument('--year', action='store', default=None, type=int, help='The Lionistic year of interest. Use for e.g 2000 for the 2000/2001 year. If not supplied, the current year will be used')
    args = parser.parse_args()

    md_name = args.md
 
    # attempt to read db conf file. If it doesn't exist, exit
    import ConfHandler
    conf = ConfHandler.ConfHandler('db_settings.ini')
    if conf.error:
        print conf.error
        exit(1)
    try:
        # read in DB settings. 
        conf.read_section('DB', 'db', ['username', 'password', 'host', 'schema', 'db_type'])
        # Allow optional MD to use, specified by name. If not supplied, use the first MD found in the db
        conf.read_section('MD', 'md', [], ['name'], optional=True)
        db_parms = conf.parms['db']
    except ConfHandler.ConfException:
        print conf.error
        exit(1)

    # attempt to read conf file. If it doesn't exist, print a warning, but continue
    conf = ConfHandler.ConfHandler('settings.ini')
    authors = []
    
    if conf.error:
        print 'Cannot find settings.ini file. Only command line configuration options will be used.'
    else:
        #find all authors from ini file, using sections of name Author n, starting from 1
        i = 1
        while True:
            try:
                conf.read_section('Author %d' % i, 'auth_%d' % i, ['name', 'title', 'email'])
                c = conf.parms['auth_%d' % i]
                authors.append([c['name'], c['title'], c['email']])
                i += 1
            except ConfHandler.ConfException:
                # print 'Could not process Author %d section in the settings.ini file. Either it has an error or does not exist' % i
                break

        # if md_name hasn't been set, try and get it from the conf file
        if not md_name:
            if 'md' in conf.parms and 'name' in conf.parms['md']:
                md_name = conf.parms['md']['name']
            else:
                print 'No MD name supplied on the command line or the settings.ini file. Will use the first MD found in the database.'

    ret = build_directories(db_parms, authors, md_name, args.year)
    if TIME_RUN:
        expired = clock() - start_time
        print 'Time expired: %02.2f' % (expired)
    exit(ret)
