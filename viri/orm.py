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


class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        from collections import OrderedDict

        fields = OrderedDict()
        for name, val in attrs.items():
            if isinstance(val, Property):
                fields[name] = val
        attrs['_fields_'] = fields
        return super().__new__(name, bases, attrs)


class Model:
    """Handler for a database table. The way it works is to only use class
    methods. This means that instances will never be created, so usage will
    look like this examples:
    >>> MyModel.create(db, {'prop1': 'val1', 'prop2': 'val2'})
    >>> MyModel.get(db, where='pk = 1')
    {'pk': 1, 'prop1': 'val1'}
    """
    __metaclass__ = ModelMeta

    @classmethod
    def table_name(cls):
        return cls.__name__.lower()

    @classmethod
    def fields(cls):
        for attr_name in dir(cls):
            obj = getattr(cls, attr_name)
            if isinstance(obj, Property):
                obj.field_name = attr_name
                yield obj

    @classmethod
    def create_table(cls, db):
        db.execute("CREATE TABLE {table_name} ({fields_def});" % dict(
            table_name=cls.table_name(),
            fields_def=','.join([' '.join(cls._fields_.items())])))

    @classmethod
    def create(cls, db, vals):
        db.execute(
            "INSERT INTO {table_name} ({field_names}) VALUES ({values});" % \
            dict(
                table_name=cls.table_name(),
                field_names=','.join([n for n in cls._fields_.keys()]),
                values=','.join([f.escape(vals[n]) \
                    for n, f in cls._fields_.items()])))
        return vals

    @classmethod
    def query(cls, db, where=None, order=None):
        sql = "SELECT {fields} FROM {table_name}" % dict(
            fields=','.join(cls._fields_.keys()),
            table_name=cls.table_name())

        if where:
            sql += " WHERE"
            for field, val in where.items:
                sql += " {0} {1} AND" % (field,
                    cls._fields_[field.split(' ')[0]].escape(val))
            sql = sql[:-4]

        if order:
            sql += " ORDER BY {0}" % ','.join(order)

        return db.query(sql)

    @classmethod
    def get(cls, db, where):
        return cls.query(db, where)[0]


class Property:
    """Handler for a database field"""
    def __init__(self, required=True):
        self.required = required

    def escape(self, val):
        return val

    def field_type(self):
        raise NotImplementedError('Properties must implement a field_type' \
            ' method')

    @property
    def field_def(self):
        return ''.join(( 
            self.field_type(),
            "" if self.required else " NULL"))


class BooleanProperty(Property):
    def escape(self, val):
        return "TRUE" if val else "FALSE"

    def field_type(self):
        return "BOOL"


class EscapedProperty(Property):
    def escape(self, val):
        return "'%s'" % val.replace("'", "''")


class CharProperty(EscapedProperty):
    def __init__(self, size, required=True):
        self.size = size
        super().__init__(required)

    def field_type(self):
        return "VARCHAR({0})" % self.size


class TextProperty(EscapedProperty):
    def escape(self, val):
        super().escape(str(val))

    def field_type(self):
        return "LONGTEXT"


class DatetimeProperty(EscapedProperty):
    def __init__(self, auto=False, required=True):
        self.auto = auto
        super().__init__(required)

    def escape(self, val):
        import datetime
        if self.auto:
            val = datetime.datetime.now()
        return "'{0}'" % val.strftime('%Y-%m-%d %H:%M:%S')

    def field_type(self):
        return "DATETIME"

