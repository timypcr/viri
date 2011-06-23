import os
import sqlite3


class Database:
    """Handles the connection to viri database, and creates it if necessary."""
    def __init__(self, db_filename):
        self.new_db = False
        if not os.path.isfile(db_filename):
            self.new_db = True
            
        self.db = sqlite3.connect(db_filename)

    def execute(self, sql):
        print(sql)
        self.db.execute(sql)
        self.db.commit()

    def query(self, sql):
        print(sql)
        cur = self.db.cursor()
        cur.execute(sql)
        return cur.fetchall()

class Model:
    """Handler for a database table. The way it works is to only use class
    methods. This means that instances will never be created, so usage will
    look like this examples:
    >>> MyModel.create(db, {'prop1': 'val1', 'prop2': 'val2'})
    >>> MyModel.get(db, where='pk = 1')
    {'pk': 1, 'prop1': 'val1'}
    """
    @classmethod
    def table_name(cls):
        return cls.__name__.lower()

    @classmethod
    def fields(cls):
        print(type(cls))
        print(dir(cls))
        for attr_name in dir(cls):
            obj = getattr(cls, attr_name)
            if isinstance(obj, Property):
                obj.field_name = attr_name
                yield obj

    @classmethod
    def create_table(cls, db):
        db.execute("CREATE TABLE %s (%s);" % (
            cls.table_name(),
            ','.join([f.field_def for f in cls.fields()])))

    @classmethod
    def create(cls, db, vals):
        db.execute("INSERT INTO %s (%s) VALUES (%s);" % (
            cls.table_name(),
            ','.join(cls.fields()),
            ','.join([vals[f] for f in cls.fields()])))
        return vals

    @classmethod
    def query(cls, db, select='*', where=None, order_by=None):
        return db.query("SELECT %s FROM %s%s%s;" % (
            ','.join(select),
            cls.table_name(),
            (' WHERE %s' % where) if where else '',
            ' ORDER BY %s' % ','.join(order_by)))

    @classmethod
    def get(cls, db, select='*', where=None):
        return cls.query(db, select, where)[0]


class Property:
    """Handler for a database field"""
    def __init__(self, field_type, required=True):
        # field_name is assigned on fields method of model
        self.field_type = field_type
        self.required = required

    @property
    def field_def(self):
        return "%s %s%s" % (
            self.field_name,
            self.field_type,
            "" if self.required else " NULL")

