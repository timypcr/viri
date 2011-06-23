import datetime
import traceback
from hashlib import sha1
from viri.orm import Model, Property


class GenericFile(Model):
    """This model represents the base class for both scripts and data files,
    defining common fields used for any file. This model is not used directly,
    only subclasses Script and DataFile are instantiated.
    """
    filename = Property('varchar(255)')
    content = Property('longtext')
    saved = Property('datetime')

    @classmethod
    def create(cls, db, vals):
        vals['saved'] = datetime.datetime.now()
        Model.create(db, vals)


class Script(GenericFile):
    script_id = Property('varchar(255)')

    @classmethod
    def create(cls, db, vals):
        vals['script_id'] = sha1(vals['content']).hexdigest()
        GenericFile.create(db, vals)

    @classmethod
    def execute(cls, script_id):
        exec(cls.code_by_id(script_id))
        ViriScript = locals().get('ViriScript')
        try:
            return ViriScript().run()
        except:
            return traceback.format_exc()

    @classmethod
    def code_by_id(cls, script_id):
        cls.get(select='content',
            where="script_id = '%s'" % script_id)

class DataFile(GenericFile):
    last_version = Property('bool')


class Execution(Model):
    script_id = Property('varchar(255)')
    filename = Property('varchar(255)')
    success = Property('bool')
    result = Property('longtext')
    executed = Property('datetime')
    
    @classmethod
    def create(cls, db, vals):
        vals['executed'] = datetime.datetime.now()
        vals['filename'] = Script.get(select='filename',
            where="script_id = '%s'" % vals['script_id'])['filename']
        Model.create(db, vals)


class Job(Model):
    script_id = Property('varchar(255)')
    active = Property('bool')
    minute = Property('varchar(2)')
    hour = Property('varchar(2)')
    month_day = Property('varchar(2)')
    month = Property('varchar(2)')
    week_day = Property('varchar(1)')
    year = Property('varchar(4)')

    @classmethod
    def have_to_run_now(cls, db, now):
        for job in Model.query(select='*', where="active = true"):
            # In cron, Sunday is 0, but in Python is 6
            if job['minute'] in ('*', now.minute) and \
            job['hour'] in ('*', now.hour) and \
            job['month_day'] in ('*', now.day) and \
            job['month'] in ('*', now.month) and \
            job('week_day') in ('*', (now.weekday() + 1) % 7) and \
            job['year'] in ('*', now.year):
                yield job


objects = [Script, DataFile, Execution, Job]

