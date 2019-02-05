''' 
A module to interact with a database, inserting and selecting data as required.
Modules which need to do DB interaction should inherit from this module,
adding specific interaction code as required.

Author: Kim van Wyk
'''
import sqlalchemy as sa

# Exception to indicate dbhandling errors
class DBException(Exception): pass
# There is no app version supplied yet, and it is needed
class DBNoAppVersion(Exception): pass

class BaseDBHandler(object):
    ''' Instantiate an object to deal with db queries, connecting to the spec'ed db on initiation '''

    def __init__(self, db_parms, logging=False, usedb=True):
        ''' connect to the database specified in the 'db_parms' dict.
        'db_parms' must contain these keys:
        	username
                password
                host - ip address or name
                database - schema to use
        'db_parms' may also optionally contain:
                one or more entries ending in _table - specifying a table name from the db to use for a specific purpose
                for each '_table' entry, an optional entry of the same name before the "_table" suffix with a "_db" suffix
                     - specifies a schema to find the associated table in. If not supplied the schema specified in the 'database'
                     key of 'db_parms' is used.
                for each '_table' entry, an optional entry of the same name before the "_table" suffix with a "_columns" suffix
                     - specifies a set of column names to ensure are in the associated table

         Entries of name "foo_table" and "foo_columns" are provided as attributes of name "foo_t" and "foo_cols" respectively, if they are found.
         If they are not found, an error is raised

        'logging' is a boolean flag to toggle output of SQL commands if true
        'usedb' is a debug flag to turn off any db interaction if true, useful for debug in the caller
        If an error occurs, the 'error' attribute is populated with a string giving details and None is returned. 
        Callers should check if 'error' is non-None, and if so, report the error in an appropriate manner
        DBException is not raised, to allow the caller to receive a DBHandler object it can check for the 'error' attribute without
        needing additional exception handling of its own.
        '''
        self.error = None
        self.usedb = usedb
        if not self.usedb:
            return
        # Connect to db
        try:
            # use a short connection timeout to not have to wait too long if the db is unavailable
            self.engine = sa.create_engine('mysql://%(username)s:%(password)s@%(host)s/%(database)s?connect_timeout=5' % (db_parms), echo=logging)
            # obtain and bind metadata for the created engine, to use when creating the needed tables
            md = sa.MetaData()
            md.bind = self.engine
            # Attempt a "SHOW DATABASES query, to check this connection is valid
            from sqlalchemy.sql import text
            s = text('SHOW DATABASES')
            ret = self.engine.execute(s).fetchall()
        except:
            self.error = 'Could not connect to %(database)s db at host %(host)s with username %(username)s' % (db_parms)
            return None
        
        # instantiate tables to an attr of the same name with a trailing _t, using the spec'ed alternate db if one is supplied
        ts = [t[:-6] for t in db_parms.keys() if t[-6:] == '_table']
        for table in ts:
            try:
                tname = sa.Table(db_parms['%s_table' % table], md, autoload=True, schema=db_parms.get('%s_db' % table, db_parms['database']))
                setattr(self, '%s_t' % table, tname)
            except:
                self.error = 'Could not read details of table %s from database' % db_parms['%s_table' % table]
                return None

        # for any required lists of columns, check that their associated table exists and holds those columns.
        # provide the verified list of cols in an attr of the same name, with a trailing _cols

        # obtain a list of tuples, of form (table attr, col-list-name)
        cls = [(getattr(self, '%s_t' % t[:-8]), t) for t in db_parms.keys() if t[-8:] == '_columns' and hasattr(self, '%s_t' % t[:-8])]
        for (t, cols_name) in cls:
            try:
                # obtain value of column list
                cols = db_parms[cols_name].split(',')
                # Determine if cols list is empty, creating an empty list if so
                if len(cols) == 1 and not cols[0].strip():
                    cols = []
            except:
                self.error = 'Could not parse the list of columns specified as "%s" in the ini file into a usable format' % (cols_name)
                return None
            

            # determine if each supplied column is in the specified table
            for col in cols:
                if col not in t.c:
                    # raise an error as a non-existent column has been specified
                    self.error = \
                        'Column "%s" specified in the "%s" setting in the "DB" section of the ini file does not exist in table "%s"' \
                        % (col, cols_name, t)
                    return None
            
            # set cols to a more useful name
            setattr(self, '%s_cols' % cols_name[:-8], cols)

        # set now to None, to ensure it is accurately set when needed
        self.now = None

    def check_table_exists(self, table_name, error_blurb):
        ''' Confirm that the variable called 'table_name' is an attr of self, otherwise raising an exception
        and adding a supplied blurb to self.error
        '''
        if not hasattr(self, table_name):
            self.error = error_blurb
            raise DBException

    def check_app_version_set(self):
        ''' Check that the object has had an attribute set to hold the app version, for use in various table ops
        '''
        if not hasattr(self, 'appversion'):
            raise DBNoAppVersion

