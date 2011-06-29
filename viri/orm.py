
class Database:
    """Handles the connection to viri database, and creates it if necessary."""
    def __init__(self, db_filename):
        import os
        import sqlite3

        self.new_db = False
        if not os.path.isfile(db_filename):
            self.new_db = True
            
        self.db = sqlite3.connect(db_filename, detect_types=sqlite3.PARSE_DECLTYPES)

    def execute(self, sql, params=()):
        self.db.execute(sql, params)
        self.db.commit()

    def query(self, sql, params=()):
        cur = self.db.cursor()
        cur.execute(sql, params)
        return cur.fetchall()


class Property:
    """Handler for a database field"""
    def __init__(self, required=True):
        self.required = required

    def field_type(self):
        raise NotImplementedError('Properties must implement a field_type' \
            ' method')

    @property
    def field_def(self):
        return ''.join(( 
            self.field_type(),
            "" if self.required else " NULL"))


class BooleanProperty(Property):
    def field_type(self):
        return "BOOL"


class CharProperty(Property):
    def __init__(self, size, required=True):
        self.size = size
        super().__init__(required)

    def field_type(self):
        return "VARCHAR({})".format(self.size)


class TextProperty(Property):
    def field_type(self):
        return "LONGTEXT"


class DatetimeProperty(Property):
    def field_type(self):
        return "TIMESTAMP"


class Result:
    def __init__(self, fields, row):
        self.fields = fields
        self.row = row

    def __str__(self):
        return '\t'.join(map(str, self.row))

    def __getattr__(self, attr):
        return self.row[self.fields.index(attr)]

    def __getitem__(self, item):
        return self.row[item]


class ResultSet:
    def __init__(self, fields, results):
        self.fields = fields
        self.results = results

    def __str__(self):
        return '\n'.join(map(str, self))

    def __bool__(self):
        return bool(self.results)

    def __iter__(self):
        for row in self.results:
            yield Result(self.fields, row)

    def __getitem__(self, item):
        result = Result(self.fields, self.results[item])
        return result

class ModelMeta(type):
    def __new__(cls, name, bases, attrs):
        from collections import OrderedDict

        attrs['_fields_'] = OrderedDict()

        for base in reversed(bases):
            attrs['_fields_'].update(base._fields_)

        for key, val in attrs.items():
            if isinstance(val, Property):
                attrs['_fields_'][key] = val

        res = super().__new__(cls, name, bases, attrs)
        return res


class Model(metaclass=ModelMeta):
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
    def field_names(cls):
        return list(cls._fields_.keys())

    @classmethod
    def create_table(cls, db):
        field_defs = []
        for field in cls.field_names():
            field_defs.append(
                '{} {}'.format(field, cls._fields_[field].field_def))
        db.execute("CREATE TABLE {table} ({field_defs});".format(
            table=cls.table_name(),
            field_defs=','.join(field_defs)))

    @classmethod
    def create(cls, db, vals):
        fields = cls.field_names()
        values = [vals[n] for n in fields]
        db.execute(
            "INSERT INTO {table} ({fields}) VALUES ({values});".format(
                table=cls.table_name(),
                fields=','.join(fields),
                values=','.join(['?'] * len(fields))),
            values)
        return Result(fields, values)

    @classmethod
    def query(cls, db, fields=None, where=None, order=None):
        if not fields:
            fields = cls.field_names()

        sql = "SELECT {fields} FROM {table}".format(
            fields=','.join(fields),
            table=cls.table_name())

        if where:
            sql += " WHERE"
            for field, val in where.items():
                sql += " {} ? AND".format(field)
            sql = sql[:-4]

        if order:
            sql += " ORDER BY {}".format(','.join(order))

        return ResultSet(fields, db.query(sql, tuple(where.values())))

    @classmethod
    def get(cls, db, fields=None, where=None):
        result = cls.query(db, fields, where)
        return result[0] if result else None

