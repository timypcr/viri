from viri import orm


class GenericFile(orm.Model):
    """This model represents the base class for both scripts and data files,
    defining common fields used for any file. This model is not used directly,
    only subclasses Script and DataFile are instantiated.
    """
    filename = orm.CharProperty(size=255)
    content = orm.TextProperty()
    saved = orm.DatetimeProperty(auto=True)


class Script(GenericFile):
    script_id = orm.CharProperty(size=255)

    @classmethod
    def create(cls, db, vals):
        from hashlib import sha1

        vals['script_id'] = sha1(vals['content']).hexdigest()
        super().create(db, vals)

    @classmethod
    def execute(cls, script_id):
        import traceback

        exec(cls.code_by_id(script_id))
        ViriScript = locals().get('ViriScript')
        try:
            return ViriScript().run()
        except:
            return traceback.format_exc()

    @classmethod
    def code_by_id(cls, script_id):
        return cls.get(where={"script_id =": script_id}).content


class DataFile(GenericFile):
    last_version = orm.BooleanProperty()


class Execution(orm.Model):
    script_id = orm.CharProperty(size=255)
    filename = orm.CharProperty(size=255)
    success = orm.BooleanProperty()
    result = orm.TextProperty()
    executed = orm.DatetimeProperty(auto=True)
    
    @classmethod
    def create(cls, db, vals):
        vals['filename'] = Script.get(
            where={"script_id =": vals['script_id']}).filename
        super().create(db, vals)


class Job(orm.Model):
    script_id = orm.CharProperty(size=255)
    active = orm.BooleanProperty()
    minute = orm.CharProperty(size=2)
    hour = orm.CharProperty(size=2)
    month_day = orm.CharProperty(size=2)
    month = orm.CharProperty(size=2)
    week_day = orm.CharProperty(size=1)
    year = orm.CharProperty(size=4)

    @classmethod
    def run_now(cls, db, now):
        for job in orm.Model.query(where={"active =": True}):
            # In cron, Sunday is 0, but in Python is 6
            if job['minute'] in ('*', now.minute) and \
            job['hour'] in ('*', now.hour) and \
            job['month_day'] in ('*', now.day) and \
            job['month'] in ('*', now.month) and \
            job('week_day') in ('*', (now.weekday() + 1) % 7) and \
            job['year'] in ('*', now.year):
                yield job


objects = [Script, DataFile, Execution, Job]

