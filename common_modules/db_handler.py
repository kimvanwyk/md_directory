import ConfigParser
from enum import Enum
import operator
from pprint import pprint

import attr
from sqlalchemy import create_engine, Table, MetaData, and_, or_, select

from utilities import get_current_year

HANDLE_EXC = True
MEMBER_PHS = ['home_ph', 'bus_ph', 'cell_ph', 'fax']
PREV_TITLES = (('PID','International Director'), ('PCC', 'Council Chairperson'), ('PDG', 'District Governor'))

TABLE_PREFIX = 'md_directory'

MEMBER_IDS = {'Kim': 2602128,
       'Vicki': 2352224,
       'Denis': 666898,
       'Alistair': 903648,
       'Avril': 4200750,
       'Trevor': 709888,
       'Phil': 2687992,
       'Yolandi': 3762497,
       'Barbara': 2680550,
       'Jacqui': 1399208,
       'Dave': 355357,
       'Neville': 3478783,
       'Beryl': 4040774,
       'Lyn': 349981,
       'Malcolm': 990112
       }

CLUB_IDS = {'North Durban': 27814,
            'Benoni Lakes': 115092
       }

class ClubType(Enum):
    lions = 1
    branch = 2
    leos = 3
    lioness = 4

@attr.s
class MultipleDistrict(object):
    id = attr.ib(factory=int)
    name = attr.ib(default=None) 
    website = attr.ib(default=None) 
    is_in_use = attr.ib(default=False)
    officers = attr.ib(factory=list)

@attr.s
class District(MultipleDistrict):
    parent = attr.ib(default=None) 

@attr.s
class Region(object):
    id = attr.ib(factory=int)
    name = attr.ib(default=None) 
    chair = attr.ib(default=None) 
    district = attr.ib(default=None)

@attr.s
class Zone(Region):
    region = attr.ib(default=None)

@attr.s
class Club(object):
    id = attr.ib(factory=int)
    club_type = attr.ib(default=ClubType.lions)
    struct = attr.ib(default=None)
    prev_struct = attr.ib(default=None)
    name = attr.ib(default=None)
    meeting_time = attr.ib(default=None)
    meeting_address = attr.ib(factory=list)
    postal_address = attr.ib(factory=list)
    charter_year = attr.ib(factory=int)
    website = attr.ib(default=None)
    is_suspended = attr.ib(default=False)
    zone = attr.ib(default=None)
    is_closed = attr.ib(default=False)
    officers = attr.ib(factory=list)

@attr.s
class Member(object):
    id = attr.ib(factory=int)
    first_name = attr.ib(default=None)
    last_name = attr.ib(default=None)
    is_deceased = attr.ib(default=False)
    is_resigned = attr.ib(default=False)
    partner = attr.ib(default=None)
    is_partner_lion = attr.ib(default=False)
    join_date = attr.ib(factory=int)
    home_ph = attr.ib(default=None)
    bus_ph = attr.ib(default=None)
    fax = attr.ib(default=None)
    cell_ph = attr.ib(default=None)
    email = attr.ib(default=None)
    club = attr.ib(default=None)
    title = attr.ib(default=None)


@attr.s
class Officer(object):
    title = attr.ib(default=None)
    member = attr.ib(default=None)

class DBHandler(object):
    def __init__(self, username, password, schema, host, port, db_type, year=None):
        if not year:
            year = get_current_year()
        self.year = year
        engine = create_engine('%s://%s:%s@%s:%s/%s' % (db_type, username, password, host, port, schema), echo=False)
        metadata = MetaData()
        metadata.bind = engine
        self.conn = engine.connect()
        tables = [t[0] for t in self.conn.execute('SHOW TABLES').fetchall() if TABLE_PREFIX in t[0]]
        self.tables = {}
        for t in tables:
            self.tables[t.split(TABLE_PREFIX)[-1].strip('_')] = Table(t, metadata, autoload=True, schema=schema)

        self.officer_titles = {}
        to = self.tables['officertitle']
        res = self.conn.execute(to.select()).fetchall()
        for r in res:
            year = self.year
            office_id = r.id
            if r.ip_id:
                year -= 1
                office_id = r.ip_id
            self.officer_titles[r.id] = (r.title, office_id, year)

    def __db_lookup(self, lookup_id, table, mapping, exclude=[]):
        t = self.tables[table]
        res = db.conn.execute(t.select(t.c.id == lookup_id)).fetchone()
        map = {}
        for (k,v) in res.items():
            if k not in exclude:
                map[mapping.get(k, k)] = bool(v) if '_b' in k else v
        return (map, res)

    def get_member(self, member_id, mapping={'deceased_b': 'is_deceased', 'resigned_b': 'is_resigned',
                                             'partner_lion_b': 'is_partner_lion', 'club_id': 'club'},
                   email=None):
        (map, res) = self.__db_lookup(member_id, 'member', mapping)
        map['title'] = self.get_title(member_id)
        if email:
            map['email'] = email
        m = Member(**map)
        return m

    def get_club(self, club_id, mapping={'suspended_b': 'is_suspended', 'closed_b': 'is_closed',
                                         'meet_time':'meeting_time'},
                 exclude=('parent_id', 'struct_id', 'prev_struct_id', 'type', 'add1', 'add2', 'add3',
                 'add4', 'add5', 'po_code', 'postal', 'postal1', 'postal2', 'postal3', 'postal4', 'postal5',
                 'zone_id'),
                 office_ids = {ClubType.lions: (1,2,3,4),
                               ClubType.branch: (16,1,2,3),
                               ClubType.lioness: (16,1,2,3),
                               ClubType.leos: (20,1,2,3)},
                 club_type_mapping = {0: ClubType.lions,
                                      1: ClubType.branch,
                                      2: ClubType.lioness,
                                      3: ClubType.leos}):
        (map, res) = self.__db_lookup(club_id, 'club', mapping, exclude)
        map['meeting_address'] = [res['add%s' % i] for i in xrange(1,6) if res['add%s' % i]]
        map['postal_address'] = [res['postal%s' % i] for i in xrange(1,6) if res['postal%s' % i]]
        if res['po_code']:
            map['postal_address'].append(res['po_code'])
        map['club_type'] = club_type_mapping[res['type']]

        ts = self.tables['clubofficer']
        map['officers'] = []
        for office_id_index in office_ids[map['club_type']]:
            (title, office_id, year) = self.officer_titles[office_id_index]
            res = self.conn.execute(ts.select(and_(ts.c.club_id == club_id,
                                                   ts.c.year == year,
                                                   ts.c.office_id == office_id))).fetchone()
            if res:
                map['officers'].append(Officer(title, self.get_member(res.member_id, email=res.email)))
        c = Club(**map)
        return c

    def get_region(self, region_id, exclude=('struct_id',)):
        (map, res) = self.__db_lookup(region_id, 'region', {}, exclude)
        map['district'] = self.get_struct(res['struct_id'])
        t = self.tables['regionchair']
        res = db.conn.execute(t.select(and_(t.c.parent_id == res['id'],
                                            t.c.year == self.year))).fetchone()
        if res:
            map['chair'] = self.get_member(res['member_id'], email=res['email'])
        r = Region(**map)
        return r

    def get_region_zones(self, region_id):
        t = self.tables['zone']
        res = db.conn.execute(t.select(and_(t.c.region_id == region_id,
                                            t.c.in_region_b == 1)).order_by(t.c.name)).fetchall()
        return [self.get_zone(r.id) for r in res]

    def get_zone(self, zone_id, exclude=('struct_id', 'in_region_b', 'region_id')):
        (map, res) = self.__db_lookup(zone_id, 'zone', {}, exclude)
        map['district'] = self.get_struct(res['struct_id'])
        if res['in_region_b']:
            map['region'] = self.get_region(res['region_id'])
        t = self.tables['zonechair']
        res = db.conn.execute(t.select(and_(t.c.parent_id == res['id'],
                                            t.c.year == self.year))).fetchone()
        if res:
            map['chair'] = self.get_member(res['member_id'], email=res['email'])
        z = Zone(**map)
        return z

    def get_zone_clubs(self, zone_id):
        t = self.tables['clubzone']
        res = db.conn.execute(t.select(and_(t.c.zone_id == zone_id,
                                            t.c.year == self.year))).fetchall()
        clubs = [self.get_club(r.club_id) for r in res]
        clubs.sort(key=lambda x:x.name)
        return clubs

    def get_struct(self, struct_id, mapping={'in_use_b': 'is_in_use'}, 
                   class_map={0: (District, (5,6,7,8,9,10)), 
                              1: (MultipleDistrict, (11,12,13,14,15))},
                   exclude=('parent_id', 'type_id')):
        (map, res) = self.__db_lookup(struct_id, 'struct', mapping, exclude)
        if res.parent_id:
            map['parent'] = self.get_struct(res.parent_id)
        (cls, office_ids) = class_map[res['type_id']]

        ts = self.tables['structofficer']
        map['officers'] = []
        for office_id_index in office_ids:
            (title, office_id, year) = self.officer_titles[office_id_index]
            res = self.conn.execute(ts.select(and_(ts.c.struct_id == struct_id,
                                                   ts.c.year == year,
                                                   ts.c.office_id == office_id))).fetchone()
            if res:
                map['officers'].append(Officer(title, self.get_member(res.member_id, email=res.email)))
        s = cls(**map)
        return s

    def get_struct_regions(self, struct_id):
        t = self.tables['region']
        res = db.conn.execute(t.select(t.c.struct_id == struct_id).order_by(t.c.id)).fetchall()
        return [self.get_region(r.id) for r in res]

    def get_struct_zones(self, struct_id):
        t = self.tables['zone']
        res = db.conn.execute(t.select(t.c.struct_id == struct_id).order_by(t.c.id)).fetchall()
        return [self.get_zone(r.id) for r in res]

    def get_title(self, member_id, 
                  struct_officers = ((19, 0, operator.eq, "IP"),  (19, -1, operator.eq, "PIP"),  (21, 0, operator.eq, "ID"),  
                                     (21, -1, operator.eq, "ID"),  (11, 0, operator.eq, "CC"),  (5, 0, operator.eq, "DG"),  
                                     (11, -1, operator.le, "PCC"),  (13, 0, operator.eq, "CCE"),  (5, -1, operator.eq, "IPDG"),  
                                     (7, 0, operator.eq, "1VDG"),  (8, 0, operator.eq, "2VDG"),  (5, -2, operator.le, "PDG"),  
                                     (14, 0, operator.eq, "CS"),  (15, 0, operator.eq, "CT"),  (9, 0, operator.eq, "DCS"),  
                                     (10, 0, operator.eq, "DCT")),
                  club_officers = ((1, 0, operator.eq, "LP"), (2, 0, operator.eq, "LS"), 
                                   (3, 0, operator.eq, "LT"), (1, -1, operator.le, "PLP"))):
        ''' Return a title for the supplied member_id, or None
        if none found
        '''
        def search_officers(member_id, table, mapping):
            title = None
            t = self.tables[table]
            res = db.conn.execute(t.select(t.c.member_id == member_id)).fetchall()
            index = 100
            for (n,(office_id, addition, op, ttl)) in enumerate(mapping):
                for r in res:
                    if all(((office_id == r.office_id), (op(r.year, self.year + addition)),
                            (n < index))):
                        index = n
                        title = ttl
                        break
            return title

        title = search_officers(member_id, 'structofficer', struct_officers)
        if not title:
            for (table, ttl) in (('regionchair', 'RC'), ('zonechair', 'ZC')):
                t = self.tables[table]
                res = db.conn.execute(t.select(and_(t.c.member_id == member_id,
                                                    t.c.year == self.year))).fetchall()
                if res:
                    title = ttl
                    break
        if not title:
            for (type_id, ttl) in ((1, 'MDC'), (0, 'DC')):
                t = self.tables['struct']
                structs = db.conn.execute(t.select(t.c.type_id == type_id)).fetchall()
                t = self.tables['structchair']
                for struct in structs:
                    res = db.conn.execute(t.select(and_(t.c.member_id == member_id,
                                                        t.c.year == self.year,
                                                        t.c.struct_id == struct.id))).fetchall()
                    if res:
                        title = ttl
                        break
                if title:
                    break
        if not title:
            title = search_officers(member_id, 'clubofficer', club_officers)
        return title

def get_db_settings(fn='db_settings.ini', sec='DB'):
    settings = {}
    cp = ConfigParser.SafeConfigParser()
    with open(fn, 'r') as fh:
        cp.readfp(fh)
    for opt in cp.options(sec):
        settings[opt] = cp.get(sec, opt)
    return settings

db = DBHandler(year=2019, **get_db_settings())
# for (k,v) in MEMBER_IDS.items():
#     print db.get_member(v)

# for (k,v) in CLUB_IDS.items():
#     print db.get_club(v)

# print db.get_struct(5)
# print db.get_struct(9)

# print db.get_region(3)
# print db.get_region(4)

# print db.get_zone(49)
# print db.get_zone(50)

# pprint(db.get_region_zones(4))
# pprint(db.get_zone_clubs(41))

pprint([r.name for r in db.get_struct_regions(9)])
pprint([z.name for z in db.get_struct_zones(9)])
