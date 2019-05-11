import ConfigParser

import attr
from sqlalchemy import create_engine, Table, MetaData, and_, or_, select

from utilities import get_current_year

HANDLE_EXC = True
MEMBER_PHS = ['home_ph', 'bus_ph', 'cell_ph', 'fax']
PREV_TITLES = (('PID','International Director'), ('PCC', 'Council Chairperson'), ('PDG', 'District Governor'))

TABLE_PREFIX = 'md_directory'

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

class DBHandler(object):
    def __init__(self, username, password, schema, host, port, db_type):
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
        m = Member(**map)
        return m

def get_db_settings(fn='db_settings.ini', sec='DB'):
    settings = {}
    cp = ConfigParser.SafeConfigParser()
    with open(fn, 'r') as fh:
        cp.readfp(fh)
    for opt in cp.options(sec):
        settings[opt] = cp.get(sec, opt)
    return settings

db = DBHandler(**get_db_settings())
m = db.get_member(2602128)
print m

