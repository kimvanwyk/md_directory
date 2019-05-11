import ConfigParser
import operator

import attr
from sqlalchemy import create_engine, Table, MetaData, and_, or_, select

from utilities import get_current_year

HANDLE_EXC = True
MEMBER_PHS = ['home_ph', 'bus_ph', 'cell_ph', 'fax']
PREV_TITLES = (('PID','International Director'), ('PCC', 'Council Chairperson'), ('PDG', 'District Governor'))

TABLE_PREFIX = 'md_directory'

IDS = {'Kim': 2602128,
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

    def get_member(self, member_id, mapping={'deceased_b': 'is_deceased', 'resigned_b': 'is_resigned',
                                             'partner_lion_b': 'is_partner_lion', 'club_id': 'club'}):
        t = db.tables['member']
        res = db.conn.execute(t.select(t.c.id == member_id)).fetchone()
        map = {}
        for (k,v) in res.items():
            map[mapping.get(k, k)] = bool(v) if '_b' in k else v
        map['title'] = self.get_title(member_id)
        m = Member(**map)
        return m

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
            t = db.tables[table]
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
                t = db.tables[table]
                res = db.conn.execute(t.select(and_(t.c.member_id == member_id,
                                                    t.c.year == self.year))).fetchall()
                if res:
                    title = ttl
                    break
        if not title:
            for (type_id, ttl) in ((1, 'MDC'), (0, 'DC')):
                t = db.tables['struct']
                structs = db.conn.execute(t.select(t.c.type_id == type_id)).fetchall()
                t = db.tables['structchair']
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
for (k,v) in IDS.items():
    # print k, db.get_title(v)
    print db.get_member(v)

