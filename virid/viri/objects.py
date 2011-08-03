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

from viri import orm

EXECUTION_LOG_MSG = 'Script {} with id {} executed with result: {}'

class File(orm.Model):
    """This model represents a file, which can be a Python script, or also a
    data file. The file has an id, which is a hash of the file content."""
    file_id = orm.CharProperty(size=40)
    file_name = orm.CharProperty(size=255)
    content = orm.TextProperty()
    saved = orm.DatetimeProperty()

    class Missing(Exception):
        """An exception raised when a file is requested but is missing
        from the database."""
        pass

    class InvalidScript(Exception):
        """An exception raised when a file is executed, but it's not an
        executable Python script."""
        pass

    @classmethod
    def create(cls, db, vals):
        """Overrides the default create method, calculating the file id, and
        the saved date and time."""
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
    def exists(cls, db, file_id):
        """Returns True if a file with the specified id exists."""
        res = cls.get(db, where=({"file_id =": file_id}))
        if res: return res['file_name']
        else: return None

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
            raise cls.InvalidScript(
                'ViriScript class does not have a run method')

        try:
            result = ViriScript().run(*args)
            return (True, result)
        except:
            return (False, get_internal_traceback(path))

    @classmethod
    def execute(cls, db, file_name_or_id, args, context):
        """Executes a Python script saved as a File, saving it to a temporary
        directory to import it. Exceptions are captured and returned as
        strings. All executions are recorded in the log."""
        import os
        import shutil
        import logging
        import tempfile

        success = False
        temp_dir = tempfile.mkdtemp(prefix='viri_exec_')
        script = cls.get_obj(db, file_name_or_id)
        mod_name = os.path.splitext(script['file_name'])[0]
        cls.save_content(db, file_name_or_id,
            os.path.join(temp_dir, script['file_name']))

        try:
            success, result = cls._run_script(temp_dir, mod_name, args, context)
        except Exception as exc:
            success = False
            result = str(exc)

        if success:
            logging.info(EXECUTION_LOG_MSG.format(
                script['file_name'], script['file_id'], 'SUCCESS'))
        else:
            logging.warn(EXECUTION_LOG_MSG.format(
                script['file_name'], script['file_id'], 'ERROR') +
                '\n{}'.format(result))

        shutil.rmtree(temp_dir)

        return (success, result)

    @classmethod
    def get_obj(cls, db, file_name_or_id):
        """Returns the File with the specified file id, or the latest
        uploaded file matching the file name."""
        file_obj = cls.get(db,
            where=({"file_id =": file_name_or_id}))

        if not file_obj:
            where = {'file_name =': file_name_or_id}
            last_date = cls.get(db, ("MAX(saved)",), where=where)
            if last_date:
                where.update({'saved =': last_date["MAX(saved)"]})
                file_obj = cls.get(db, where=where)

        if not file_obj:
            raise cls.Missing()

        return file_obj

    @classmethod
    def get_content(cls, db, file_name_or_id):
        """Returns the file content of the file specified by the file id,
        or the latest uploaded file matching the file name."""
        return cls.get_obj(db, file_name_or_id)['content']

    @classmethod
    def save_content(cls, db, file_name_or_id, path):
        """Saves a file to the disk, in the location specified by path.
        The file has to be specified by the file id, or the latest uploaded
        file matching the file name will be uploaded."""
        with open(path, 'wb') as f:
            f.write(cls.get_content(db, file_name_or_id))


objects = [File]

