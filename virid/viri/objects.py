from viri import orm


class File(orm.Model):
    """This model represents both scripts and data files.
    """
    file_id = orm.CharProperty(size=40)
    file_name = orm.CharProperty(size=255)
    content = orm.TextProperty()
    saved = orm.DatetimeProperty()

    class Missing(Exception):
        pass

    class InvalidScript(Exception):
        pass

    @classmethod
    def create(cls, db, vals):
        import datetime
        from hashlib import sha1

        file_id = sha1(vals['content']).hexdigest()
        file_obj = cls.get(db, where=({"file_id =": file_id}))
        if file_obj:
            return file_obj
        else:
            vals['saved'] = datetime.datetime.now()
            vals['file_id'] = file_id
            return super().create(db, vals)

    @classmethod
    def _run_script(cls, temp_dir, mod_name, args, context):
        import imp

        def get_internal_traceback(path):
            import os
            import sys
            import traceback

            PATH_PATTERN = 'File "{}", line '
            FROM = PATH_PATTERN.format(path)
            TO = PATH_PATTERN.format(os.path.basename(path))

            etype, value, tb = sys.exc_info()
            tb_list = traceback.format_exception(etype, value, tb)
            tb_list.pop(1)
            return ''.join(map(lambda x: x.replace(FROM, TO), tb_list))

        try:
            file_obj, path, desc = imp.find_module(mod_name, [temp_dir])
        except ImportError:
            raise cls.InvalidScript('File is not a Python script')

        try:
            mod = imp.load_module(mod_name, file_obj, path, desc)
        except:
            return (False, get_internal_traceback(path))
        finally:
            file_obj.close()

        if not hasattr(mod, 'ViriScript'):
            raise cls.InvalidScript('Script does not have a ViriScript class')

        ViriScript = type('ViriScript', (mod.ViriScript,), context)

        if not hasattr(ViriScript, 'run') or \
            not hasattr(ViriScript.run, '__call__'):
            raise cls.InvalidScript('ViriScript does not have a run method')

        try:
            result = ViriScript().run(*args)
            return (True, result)
        except:
            return (False, get_internal_traceback(path))

    @classmethod
    def execute(cls, db, file_name_or_id, args, context):
        import os
        import datetime
        import shutil
        import tempfile

        success = False
        temp_dir = tempfile.mkdtemp(prefix='viri_exec_')
        script = cls.get_obj(db, file_name_or_id)
        mod_name = os.path.splitext(script.file_name)[0]
        cls.save_content(db, file_name_or_id,
            os.path.join(temp_dir, script.file_name))

        try:
            success, result = cls._run_script(temp_dir, mod_name, args, context)
        except Exception as exc:
            success = False
            result = str(exc)

        #shutil.rmtree(temp_dir)

        Execution.create(db, dict(
                file_id=script.file_id,
                file_name=script.file_name,
                success=success,
                result=result,
                executed=datetime.datetime.now()))

        return (success, result)

    @classmethod
    def get_obj(cls, db, file_name_or_id):
        file_obj = cls.get(db,
            where=({"file_id =": file_name_or_id}))

        if not file_obj:
            where = {'file_name =': file_name_or_id}
            last_date = cls.get(db, ('MAX(saved)',), where=where)[0]
            where.update({'saved =': last_date})
            file_obj = cls.get(db, where=where)

        if not file_obj:
            raise cls.Missing()

        return file_obj

    @classmethod
    def get_content(cls, db, file_name_or_id):
        return cls.get_obj(db, file_name_or_id).content

    @classmethod
    def save_content(cls, db, file_name_or_id, path):
        with open(path, 'wb') as f:
            f.write(cls.get_content(db, file_name_or_id))


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

