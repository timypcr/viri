import os
import datetime
import sqlite3
from hashlib import sha1

class Property:
    """Handler for a database field"""
    def __init__(self, field_type, required=True):
        self.field_type = field_type
        self.required = required

    @property
    def field_name(self):
        return self.__class__.__name__.lower(),

    @property
    def field_def(self):
        return '%s %s %s' % (
            self.field_name,
            self.field_type,
            "" if self.required else " NULL")


class Model:
    """Handler for a database table"""
    @property
    @classmethod
    def table_name(cls):
        return cls.__name__.lower()

    @classmethod
    def fields(cls):
        for attr in cls.attrs:
            if isinstance(attr, Property):
                yield attr.__name__
    
    @classmethod
    def table_def(cls):
        return "CREATE TABLE %s (%s);" % (
            cls.table_name,
            ','.join([f.field_def for f in cls.fields]))

    @classmethod
    def create(cls, **kwargs):
        if set(cls.fields) == set(kwargs.keys()):
            "INSERT INTO %s (%s) VALUES (%s);"
        else:
            raise Exception() # FIXME custom exception with desc

    @classmethod
    def query(cls, select='*', where=None, order_by=None):
        return "SELECT %s FROM %s%s%s;" % (
            ','.join(select),
            cls.table_name,
            ' WHERE %s' % where if where else '',
            ' ORDER BY %s' % order_by if order_by else '')
        

class GenericFile(Model):
    filename = Property('varchar(255)')
    content = Property('longtext')
    saved = Property('datetime')

    @classmethod
    def create(cls, **kwargs):
        kwargs['saved'] = datetime.datetime.now()
        Model.create(**kwargs)

class DataFile(GenericFile):
    last_version = Property('bool')


class Script(GenericFile):
    script_id = Property('varchar(255)')

    @classmethod
    def create(cls, **kwargs):
        kwargs['script_id'] = sha1(kwargs['content']).hexdigest()
        GenericFile.create(**kwargs)

class Execution(Model):
    script_id = Property('varchar(255)')
    filename = Property('varchar(255)')
    success = Property('bool')
    result = Property('longtext')
    executed = Property('datetime')
    
    @classmethod
    def create(cls, **kwargs):
        kwargs['executed'] = datetime.datetime.now()
        kwargs['filename'] = '' # FIXME
        Model.create(kwargs)

class ViriDb:
    """Handles the connection to viri database, and creates it if necessary."""
    def __init__(self, db_filename):
        if os.path.isfile(db_filename):
            self.db = sqlite3.connect(db_filename)
        else:
            self.db = sqlite3.connect(db_filename)
            for model in (DataFile, Script, Execution):
                self.db.execute(
                    model.table_def([f.field_def for f in model.fields]))
            self.db.commit()

    def execute(self, sql):
        return self.db.execute(sql)


if __name__ == '__main__':
    dh = ViriDb('viri.db')

