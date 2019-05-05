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
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import orm_settings 
from utilities import get_current_year

d = {'DATABASES': orm_settings.get_db_dict()}

settings.configure(**d)

import models
from django.db.models import Q

HANDLE_EXC = True
MEMBER_PHS = ['home_ph', 'bus_ph', 'cell_ph', 'fax']
PREV_TITLES = (('PID','International Director'), ('PCC', 'Council Chairperson'), ('PDG', 'District Governor'))

def get_member_data(member_id, overrides={}):
    ''' Return formatted member data for the given id, in a dict:
    {'name':  string of the members name
    {'id': member id
    'prev_title': the previous title, if they have one. '' otherwise
    'partner': string of the partners name, or ''
    'partner_lion': Boolean if partner is a Lion or not
    'resigned': Boolean
    'join_date': int of the joining year
    'deceased': Boolean
    'country': string of country or ''
    'phone': list of phone numbers: [home, work, cell, fax] - '' for empty ones
    'email': string of email or ''
    'club': string of club name or ''}
    This allows a caller to pad blanks if it uses the result in columns

    'overrides' is a dict of fields which can override the members base field.
    This can have keys:
        email
        office
        home_ph
        fax

    'use_prev_title' governs whether to prepend (I)PID, (I)PCC or (I)PDG if applicable

    return None if the id isn't found
    '''

    try:
        m = models.Member.objects.get(pk=int(member_id))
    except:
        if not HANDLE_EXC: raise
        return None

    # look up previous title, if they have one
    prev_title = ''
    # get immediate_past year
    imm_year = get_current_year() - 1

    # look up any previous titles the member may hold
    prev_titles = models.StructOfficer.objects.filter(member__id=member_id)
    # loop over possible past titles, selecting the first that matches
    for abbrev, title in PREV_TITLES:
        try:
            item = prev_titles.filter(office__title=title)
            if item:
                item = item[0]
                if (item.year <= imm_year):
                    # found match. Check if it is Immediate Past
                    if item.year == imm_year:
                        prev_title += 'I'
                    prev_title += abbrev
                    break
        except ObjectDoesNotExist:
            # could not find item, move to next title
            pass 
    d = {}
    d['id'] = member_id
    d['prev_title'] = prev_title

    # got a valid member, build some info
    d['name'] = '%s %s' % (m.first_name, m.last_name)
    d['partner'] = m.partner.strip() or ''
    d['partner_lion'] = m.partner_lion_b
    d['resigned'] = m.resigned_b
    d['deceased'] = m.deceased_b
    d['join_date'] = m.join_date

    d['phone'] = []
    for p in MEMBER_PHS:
        if p in overrides:
            num = overrides[p]
        else:
            num = getattr(m, p)
        if num:
            # Append a phone number, using the first initial of its attr name as a label
            d['phone'].append('%s' % num)
        else:
            d['phone'].append('')

            
    d['email'] = overrides.get('email', '') or (m.email or '')

    try:
        club = m.club
        d['club'] = club.__unicode__()
    except:
        d['club'] = None
    return d

def get_md(name=None):
    ''' Return the MD Struct object specified by name. Return None if that name
    does not match an MD.
    If no name is specified, return the first MD in the db, sorted by id. If there aren't any, return None
    '''
    try:
        if name:
            # find the matching MD
            md = models.Struct.objects.get(name=name)
            if md.type.id != 1:
                # this is not an MD, raise a ValueError to let the exception dump us out
                raise ValueError
            return md
        else:
            # get the first md in the list
            return models.Struct.objects.filter(type=1)[0]
    except:
        # No match, return None
        if not HANDLE_EXC: raise
        return None

def get_struct_details(struct_id):
    ''' Return details of an struct and children within it, in a dict of:
    {'struct': struct dict for struct,
    'children': A list of struct dicts for each child in the struct}
    
    A struct dict is defined as:
    {'id': ID,
    'struct': The struct object,
     'name': Name,
     'website': Website,
     'type': Struct type
     'parent': 'id of parent, or None if there isn't one'
    }     
    '''
    try: 
        struct = models.Struct.objects.get(id=struct_id)
    except Exception:
        if not HANDLE_EXC: raise
        return None
    out = {}
    structs = [struct] + [d for d in models.Struct.objects.filter(parent=struct) if d.in_use_b]
    for s in structs:
        item = {'id': s.id,
                'struct': s,
                 'name': s.__unicode__(),
                 'website': s.website,
                 'type': s.type,
                 'parent': s.parent
                }
        if s.type.id == 1:
            out['struct'] = item
        else:
            l = out.get('children', [])
            l.append(item)
            out['children'] = l
    return out

def get_struct_officers(offices, struct_id):
    ''' For the passed in list of office titles in 'offices',
    return a list of member dicts in the same order, for officers
    of the struct from 'struct_id'.
    Each item of 'offices' may be a title string, or a tuple of (title, year of service).
    If just a string, the current year is used.
    Use None if any office doesn't find a match
    '''
    out = []
    override = {}
    officers = models.StructOfficer.objects
    for off in offices:
       # Check if off is a string
        if hasattr(off, 'upper'):
            year = get_current_year()
        else:
            off, year = off[0], off[1]
        try:
            o = officers.filter(struct__id=struct_id).filter(year=year).get(office__title=off)
            if o:
                if o.email:
                    override['email'] = o.email
                o = get_member_data(o.member.id, override)
            else:
                o = None
        except:
            if not HANDLE_EXC: raise
            o = None
        out.append(o)
    return out

def get_past_struct_officers(office, struct_id, other_structs=False, prev_structs=False, year=None):
    ''' Return a dict of 
    {'local': (year served, end month, member dict, struct name) for members who served in the specified struct
     'other':  (year served, end month, member dict, struct name) for members who served in other structs
     'prev':  (year served, end month, member dict, struct name) for members who served in pre-merged structs
     if not 'other_strucs', the 'other' key is []
    for everyone who held 'office' for the struct before 'year'. Return [] if no matches
    '''
    if not year:
        year = get_current_year()
    local_struct = models.Struct.objects.get(pk=struct_id)
    out = {}

    # A list of Q objects to filter on, the key to store them in
    items = []

    if prev_structs:
        prev_structs = [sm.previous_struct for sm in models.StructMerge.objects.filter(current_struct=struct_id)]
        items.append(((Q(struct__in=prev_structs),), 'prev'))
    else:
        prev_structs = [local_struct]
        out['prev'] = []

    items.append(((Q(struct__id=struct_id),), 'local'))
    if other_structs:
        items.append(([~Q(struct__id=struct_id),~Q(struct__in=prev_structs),
                       Q(member__club__struct=local_struct, member__deceased_b=False, member__resigned_b=False)], 'other'))
    else:
        out['other'] = []

    for qs, key in items:
        l = []
        offs = models.StructOfficer.objects.filter(*qs).filter(year__lt=year)
        offs = offs.filter(office__title=office).order_by('year', 'end_month', 'struct__name')
        for off in offs:
            l.append((off.year, off.end_month, off.member and get_member_data(off.member.id, {'email':off.email} if off.email else {}), off.struct.__unicode__()))
        out[key] = l
    return out

def get_struct_chairs(year, struct_id):
    ''' Return a list of struct chairs for a given struct and year,
    ordered by alphabetical name.
    Return tuples of (chair title, member dict)
    '''
    out = []
    chairs = models.StructChair.objects.filter(struct__id=struct_id).filter(year=year).filter(member__isnull=False)
    for c in chairs:
        out.append((c.office, get_member_data(c.member.id)))
    return out

def get_merch_centres(struct_id):
    ''' Get merch centre info for a given struct. Return a list of dicts of:
    {'manager': member dict or None,
     'fin_advisor': member dict or None,
     'contact_person': name of contact person,
     'add1' to 'add5': address lines,
     'po_code': po code,
     'tel', 'fax': phones # strings,
     'email': email,
     'website': website string}
     Return an empty list if no matches
    '''
    out = []
    mcs = models.MerchCentre.objects.filter(struct__id=struct_id)
    for mc in mcs:
        out.append({'manager': mc.manager and get_member_data(mc.manager.id),
                    'fin_advisor': mc.fin_advisor and get_member_data(mc.fin_advisor.id),
            })
        for k in ['contact_person', 'po_code', 'tel', 'fax', 'email', 'website'] + ['add%d' % i for i in range(1,6)]:
            out[-1][k] = getattr(mc, k)
    return out

def get_brightsight_offices(struct_id):
    ''' Get brightsight office info for a given struct. Return a list of dicts of:
    {'manager': name of manager,
     'manager_cell_ph': manager cell phone,
     'manager_email': manager email,
     'contact_person': name of contact person,
     'add1' to 'add5': address lines,
     'postal1' to 'postal5': address lines,
     'po_code': po code,
     'tel', 'fax': phones # strings,
     'email': email,
     'website': website string}
     Return an empty list if no matches
    '''
    out = []
    offs = models.BrightSightOffice.objects.filter(struct__id=struct_id)
    for off in offs:
        out.append({})
        for k in ['manager', 'manager_cell_ph', 'manager_email', 'contact_person', 
                  'po_code', 'tel', 'fax', 'email', 'website'] + ['add%d' % i for i in range(1,6)] + ['postal%d' % i for i in range(1,6)]:
            out[-1][k] = getattr(off, k)
    return out

def get_dist_offices(struct_id):
    ''' Get district office info for a given struct. Return a list of dicts of:
    {'contact_person': name of contact person,
     'add1' to 'add5': address lines,
     'postal1' to 'postal5': address lines,
     'po_code': po code,
     'tel', 'fax': phones # strings,
     'email': email,
     'website': website string}
     Return an empty list if no matches
    '''
    out = []
    mcs = models.DistrictOffice.objects.filter(struct__id=struct_id)
    for mc in mcs:
        out.append({})
        for k in ['contact_person', 'po_code', 'tel', 'fax', 'email', 'website'] + ['add%d' % i for i in range(1,6)] + ['postal%d' % i for i in range(1,6)]:
            out[-1][k] = getattr(mc, k)
    return out

def __get_struct_subgroup_details(group_model, chair_model, child_model, child_parent_field, name_type):
    ''' Return a closure to get details of a subgrouping of a struct
    These include regions and zones
    'group_model' is the model object of the subgroup - models.Region for eg
    'chair_model' - the model to get subgroup chair people from - models.RegionChair for eg
    'child_model' - the model holding children of the subgroup - models.Zone for eg
    'child_parent_field' - the field name in each child object which links to the subgroup - "region" for eg
    'name_type' - the attr or func of the child model to use to get its name. Treat as a func first.
                  If it isn't a func, treat as an attr
    '''
    def f(struct_id):
        out = []
        for item in group_model.objects.filter(struct__id=struct_id):
            try:
                chair = get_member_data(chair_model.objects.filter(year=get_current_year()).filter(parent=item)[0].member.id)
            except:
                if not HANDLE_EXC: raise
                chair = None
            try:
                children = []
                for child in child_model.objects.filter(**{child_parent_field:item}):
                    # attempt to interpret name type as func, otherwise as attr
                    attr = getattr(child, name_type)
                    if callable(attr):
                        children.append(attr())
                    else:
                        children.append(attr)
            except:
                if not HANDLE_EXC: raise
                children = None
            out.append({'name': item.name, 'children': children, 'chair': chair})
        return out
    return f

get_struct_region_details = __get_struct_subgroup_details(models.Region, models.RegionChair, models.Zone, "region", "name")
get_struct_zone_details = __get_struct_subgroup_details(models.Zone, models.ZoneChair, models.Club, "zone", "__unicode__")

def get_club_officers(offices, club_id):
    ''' For the passed in list of office titles in 'offices',
    return a list of member dicts in the same order, for officers
    of the club from 'club_id'.
    Each item of 'offices' may be a title string, or a tuple of (title, year of service).
    If just a string, the current year is used.
    Use None if any office doesn't find a match
    '''
    out = []
    officers = models.ClubOfficer.objects
    for off in offices:
        override = {}
        # Check if off is a string
        if hasattr(off, 'upper'):
            year = get_current_year()
        else:
            off, year = off[0], off[1]
        try:
            o = officers.filter(club__id=club_id).filter(year=year).get(office__title=off)
            if o:
                if o.email:
                    override['email'] = o.email
                if o.phone:
                    override['home_ph'] = o.phone
                if o.fax:
                    override['fax'] = o.fax                    
                o = get_member_data(o.member.id, override)
            else:
                o = None
        except:
            if not HANDLE_EXC: raise
            o = None
        out.append(o)
    return out

def get_club_info(club_id, offices):
    ''' Return info on the club given by 'club_id'
    Return a dict of:
    {'name': Club name. Include info on parent if not a regular club,
     'regular_club': Bool if a regular club or it has a parent,
     'charter_year': int of charter date, or Null,
     'zone': Zone club is in, or None,
     'region': Region club is in, or None,
     'suspended': Bool of suspension status,
     'officers': List of member dicts or None for each of the office titles in offices,
     'website': club web address, or None,
     'meeting_times': A list of meeting time strings, or [] if there aren't any,
     'address': list of ordered physical address strings, or [],
     'postal': list of ordered postal address strings, or [],
     'children': children clubs, in a dict keyed by (name of type, list of club names), or an empty dict
    }
    Return None if no matches
    '''
    try:
        club = models.Club.objects.get(pk=club_id)
    except:
        return None
    d = {}
    d['id'] = club.id
    d['name'] = club.__unicode__()
    d['regular_club'] = club.type == 0
    d['charter_year'] = club.charter_year
    try:
        d['zone'] = club.zone.name
    except:
        d['zone'] = None
    try:
        if not club.zone.in_region_b:
            raise
        d['region'] = club.zone.region.name
    except:
        d['region'] = None
    d['suspended'] = club.suspended_b
    d['website'] = club.website

    postal = []
    for attr in ['postal%d' % a for a in range(1,5)] + ['po_code']:
        if getattr(club, attr):                
            postal.append(getattr(club, attr))
    d['postal'] = postal

    add = []
    for attr in ['add%d' % a for a in range(1,6)]:
        if getattr(club, attr):
            add.append(getattr(club, attr))
    d['address'] = add

    d['officers'] = get_club_officers(offices, club_id)
    
    # find children clubs
    children = {}
    for child in models.Club.objects.filter(parent__id=club_id):
        t = models.club_types[child.type][1]
        children[t] = children.get(t, []).append(club.name)
    # sort all children lists
    for v in children.values():
        if v:
            v.sort()
    d['children'] = children
    return d

def get_clubs_in_dist(dist_id, offices, year=None):
    ''' Return a list of club dicts for all the clubs in the district given by dist_id, 
    adding the info for 'offices', getting offices for supplied year. Use the current year
    if 'year' is None
    '''
    if not year:
        year = get_current_year()
    off = []
    for o in offices:
        off.append((o, year))
    return [get_club_info(c.id, off) for c in models.Club.objects.filter(struct__id=dist_id)]

if __name__ == "__main__":
    # print get_struct_officers(['District Governor', ('District Governor', 2009), 'First Vice District Governor', 'Second Vice District Governor', 
    #                            'Cabinet Secretary', 'Cabinet Treasurer'], 5)
    # for c in get_struct_chairs(2010, 5):
    #     print c
    # for c in get_past_struct_officers('Council Chairperson', 5):
    #     print c
    # for c in get_struct_region_details(1):
    #     print c
    # print get_struct_region_details(3)
    # for c in get_struct_zone_details(3):
    #     print c

     # print get_md_details()

    for loc in ('prev',):
        #print get_past_struct_officers('District Governor', 3, True)[loc]
        # print [l for l in get_past_struct_officers('District Governor', 3, True)[loc]]
        print loc
        print '\n'.join(['%s: %s' % (o[2]['name'], o[-1]) for o in get_past_struct_officers('District Governor', 9, True, True)[loc]])
        print

    # for sm in models.StructMerge.objects.filter(current_struct=9):
    #     print sm.previous_struct
    # offs = [('Club President', 2012), ('Club Secretary', 2012)]
    # for i in (27774, 35673):
    #     d = get_club_info(i, )
    #     print d['name']
    #     for (o,t) in zip(d['officers'], offs):
    #         print t
    #         print o['name']
            
