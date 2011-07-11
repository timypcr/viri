from viri import orm


class File(orm.Model):
    """This model represents both scripts and data files.
    """
    file_id = orm.CharProperty(size=40)
    file_name = orm.CharProperty(size=255)
    content = orm.TextProperty()
    saved = orm.DatetimeProperty()

    @classmethod
    def create(cls, db, vals):
        import datetime
        from hashlib import sha1

        vals['saved'] = datetime.datetime.now()
        vals['file_id'] = sha1(vals['content']).hexdigest()
        return super().create(db, vals)

    @classmethod
    def execute(cls, db, file_name_or_id, args, context):
        import datetime
        import traceback

        success = False
        file_obj = cls.get_content(db, file_name_or_id)
        exec_locals = {}
        exec_globals = {}
        # FIXME capture syntax errors
        exec(file_obj.content, exec_locals, exec_globals)
        ViriScript = exec_globals.get('ViriScript')
        if ViriScript and hasattr(ViriScript, 'run') and \
            hasattr(ViriScript.run, '__call__'):
            exec_cls = type('ViriScript', (ViriScript,), context)
            try:
                result = exec_cls().run(*args)
                success = True
            except:
                result = traceback.format_exc()
        else:
            result = ('script file does not contain a ViriScript class '
                'or it does not have a run method')

        Execution.create(db, dict(
                file_id=file_obj.file_id,
                file_name=file_obj.file_name,
                success=success,
                result=result,
                executed=datetime.datetime.now()))

        return result

    @classmethod
    def get_content(cls, db, file_name_or_id):
        file_obj = cls.get(db,
            where=({"file_id =": file_name_or_id}))

        if not file_obj:
            where = {'file_name =': file_name_or_id}
            last_date = cls.get(db, ('MAX(saved)',), where=where)[0]
            where.update({'saved =': last_date})
            file_obj = cls.get(db, where=where)

        return file_obj


class Execution(orm.Model):
    file_id = orm.CharProperty(size=255)
    file_name = orm.CharProperty(size=255)
    success = orm.BooleanProperty()
    result = orm.TextProperty()
    executed = orm.DatetimeProperty()


class Job(orm.Model):
    file_name_or_id = orm.CharProperty(size=255)
    minute = orm.CharProperty(size=2)
    hour = orm.CharProperty(size=2)
    month_day = orm.CharProperty(size=2)
    month = orm.CharProperty(size=2)
    week_day = orm.CharProperty(size=1)
    year = orm.CharProperty(size=4)

    @classmethod
    def run_now(cls, db, now):
        for job in cls.query(db):
            # In cron, Sunday is 0, but in Python is 6
            if job.minute in ('*', now.minute) and \
            job.hour in ('*', now.hour) and \
            job.month_day in ('*', now.day) and \
            job.month in ('*', now.month) and \
            job.week_day in ('*', (now.weekday() + 1) % 7) and \
            job.year in ('*', now.year):
                yield job


objects = [File, Execution, Job]

