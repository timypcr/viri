from viri import orm


class GenericFile(orm.Model):
    """This model represents the base class for both scripts and data files,
    defining common fields used for any file. This model is not used directly,
    only subclasses Script and DataFile are instantiated.
    """
    filename = orm.CharProperty(size=255)
    content = orm.TextProperty()
    saved = orm.DatetimeProperty()

    @classmethod
    def create(cls, db, vals):
        import datetime

        vals['saved'] = datetime.datetime.now()
        return super().create(db, vals)


class Script(GenericFile):
    script_id = orm.CharProperty(size=255)

    @classmethod
    def create(cls, db, vals):
        from hashlib import sha1

        vals['script_id'] = sha1(vals['content']).hexdigest()
        return super().create(db, vals)

    @classmethod
    def execute(cls, db, filename_or_id):
        import datetime
        import traceback

        success = False
        script = cls.get_content(db, filename_or_id)
        script_locals = {}
        script_globals = {}
        exec(script.content, script_locals, script_globals)
        ViriScript = script_globals.get('ViriScript')
        if ViriScript and hasattr(ViriScript, 'run') and \
            hasattr(ViriScript.run, '__call__'):
            try:
                result = ViriScript().run()
                success = True
            except:
                result = traceback.format_exc()
        else:
            result = ('script file does not contain a ViriScript class '
                'or it does not have a run method')

        Execution.create(db, dict(
                script_id=script.script_id,
                filename=script.filename,
                success=success,
                result=result,
                executed=datetime.datetime.now()))

        return result

    @classmethod
    def get_content(cls, db, filename_or_id):
        res = None
        for field in ('filename', 'script_id'):
            res = Script.get(db,
                where=({"{} =".format(field): filename_or_id}))
            if res: break

        return res


class DataFile(GenericFile):
    @classmethod
    def get_content(cls, db, filename):
        where = {'filename =': filename}
        last_file = cls.get(db, ('MAX(saved)',), where=where)
        where.update({'saved =': last_file[0]})
        return cls.get(db, ('content',), where=where)


class Execution(orm.Model):
    script_id = orm.CharProperty(size=255)
    filename = orm.CharProperty(size=255)
    success = orm.BooleanProperty()
    result = orm.TextProperty()
    executed = orm.DatetimeProperty()


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

