# Copyright 2011, Marc Garcia <garcia.marc@gmail.com>
#
# This file is part of Viri.
#
# Viri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Viri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Viri.  If not, see <http://www.gnu.org/licenses/>.

"""Simple ORM to define Python classes that represent SQL tables and be able
to perform basic operations in a easy and Pythonic way. The ORM has a
Database object, used for handling the connection to the sqlite database,
a Model object representing a table, and some Property classes, representing
different types of fields.

Usage sample:
>>> import datetime
>>> import orm
>>>
>>> db = orm.Database('/tmp/database.sqlite')
>>>
>>> class MyModel(orm.Model):
>>>     text_field = orm.CharProperty(size=255)
>>>     long_text_field = orm.TextProperty()
>>>     boolean_field = orm.BooleanProperty()
>>>     date_field = orm.DateTimeProperty()
>>>
>>> MyModel.create_table(db)
>>> MyModel.create(dict(
>>>     text_field='hello',
>>>     long_text_field='world!',
>>>     boolean_field=True,
>>>     date_file=datetime.datetime.now()))
>>>
>>> MyModel.query(
>>>     fields=('long_text_field', 'boolean_field'),
>>>     where=dict(text_field='hello'),
>>>     order=('date_field',))
"""

class Database:
    """Handles the connections to the viri (sqlite) database,
    creating it if necessary."""
    def __init__(self, db_filename):
        import os
        self.db_filename = db_filename
        self.new_db = not os.path.isfile(db_filename)

    def _connect(self):
        import sqlite3
        return sqlite3.connect(
            self.db_filename,
            detect_types=sqlite3.PARSE_DECLTYPES + sqlite3.PARSE_COLNAMES)

    def execute(self, sql, params=()):
        """Performs an operation that modifies the content of the database."""
        conn = self._connect()
        conn.execute(sql, params)
        conn.commit()
        conn.close()

    def query(self, sql, params=()):
        """Performs an operation that gets data from the database,
        without modifying its content."""
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(sql, params)
        result = cur.fetchall()
        conn.close()
        return result


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
    """A handler for boolean fields."""
    def field_type(self):
        return "BOOL"


class CharProperty(Property):
    """A handler for text fields."""
    def __init__(self, size, required=True):
        self.size = size
        super().__init__(required)

    def field_type(self):
        return "VARCHAR({})".format(self.size)


class TextProperty(Property):
    """A handler for long text (not indexed) fields."""
    def field_type(self):
        return "LONGTEXT"


class DatetimeProperty(Property):
    """A handler for datetime fields."""
    def field_type(self):
        return "TIMESTAMP"


class ModelMeta(type):
    """Metaclass for the Model class, that creates an attribute _fields_
    containing a ordered dictionary with the field names, and the instance
    of its property."""
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
    """Handler for a database table. All methods are defined as class methods,
    so the child classes should be used directly, and not instances of them."""
    @classmethod
    def row(cls, fields, values):
        return dict(zip(fields, values))

    @classmethod
    def table_name(cls):
        """Returns the SQL table name. This is the name of the class in lower
        case."""
        return cls.__name__.lower()

    @classmethod
    def field_names(cls):
        """Returns a list containing the fields of the models. This is all
        attributes of the class which are subclasses of the Property class."""
        return list(cls._fields_.keys())

    @classmethod
    def create_table(cls, db):
        """Created the table in the database."""
        field_defs = []
        for field in cls.field_names():
            field_defs.append(
                '{} {}'.format(field, cls._fields_[field].field_def))
        db.execute("CREATE TABLE {table} ({field_defs});".format(
            table=cls.table_name(),
            field_defs=','.join(field_defs)))

    @classmethod
    def create(cls, db, vals):
        """Inserts a new row on the associated table."""
        fields = cls.field_names()
        values = [vals[n] for n in fields]
        db.execute(
            "INSERT INTO {table} ({fields}) VALUES ({values});".format(
                table=cls.table_name(),
                fields=','.join(fields),
                values=','.join(['?'] * len(fields))),
            values)
        return cls.row(fields, values)

    @classmethod
    def query(cls, db, fields=None, where={}, order=()):
        """Performs a query to the related table,
        with the specified arguments."""
        from collections import OrderedDict
        where = OrderedDict(where)
        if not fields:
            fields = cls.field_names()
        sql = "SELECT {} FROM {}".format(','.join(fields), cls.table_name())
        if where:
            sql += " WHERE " + " AND ".join(
                map(lambda x: x + " ?", where.keys()))
        if order:
            sql += " ORDER BY {}".format(','.join(order))
        return [cls.row(fields, vals) for vals in db.query(sql, tuple(where.values()))]

    @classmethod
    def get(cls, db, fields=None, where={}):
        """Performs a query to the related table, returning one or cero
        results. This should be only used when filtering by unique fields,
        or when returning a single random record is not a problem."""
        result = cls.query(db, fields, where)
        return result[0] if result else None

    @classmethod
    def delete(cls, db, where):
        """Deletes all rows matching the specified criteria from the related
        table."""
        from collections import OrderedDict
        where = OrderedDict(where)
        sql = "DELETE FROM {} WHERE ".format(cls.table_name())
        sql += " AND ".join(map(lambda x: x + " ?", where.keys()))
        db.execute(sql, tuple(where.values()))

