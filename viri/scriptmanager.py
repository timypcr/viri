import sys
import os
import datetime
import logging
import tempfile
import traceback
from hashlib import sha1
from dbhandler import Script

BASE_SCRIPT = '__base__'
TMP_DIR_PREFIX = 'viri-exec-'


class ScriptManager:
    class ExecutionError(Exception):
        """Represents any error during script execution"""
        pass

    def __init__(self, script_dir, info_dir, context):
        """Sets class attributes

        Arguments:
        context -- dictionary containing values that will be available
            as attributes of the ViriScript class in the script
        """
        self.context = context

    def get_script_id(self, filename, content):
        """Calculates a pseudo-unique hash of the script content, to be used
        as its id.

        Arguments:
        filename -- original script file name
        content -- script content (code)
        """
        return sha1(content).hexdigest()

    def _load_script(self, script_id):
        original_filename = Script.get(
            select=('filename',),
            where="script_id = '%s'" % script_id)
        script_ext = os.path.splitext(original_filename)[-1]
        tmp_dir = tempfile.mkdtemp(prefix=TMP_DIR_PREFIX)
        sys.path.append(tmp_dir)
        script_filename = os.path.join(tmp_dir, '%s%s' % (
            script_id, script_ext))
        script_mod = __import__(script_filename)
        sys.path.remove(tmp_dir)
        os.rmdir(tmp_dir)

        if not hasattr(script_mod, 'ViriScript'):
            raise self.ExecutionError('Script %s (%s) does not implement'
                ' a ViriScript class' % (original_filename, script_id))

        script_cls = script_mod.ViriScript

        if hasattr(script_cls, 'run') and hasattr(script_cls.run, '__call__'):
            return script_cls
        else:
            raise self.ExecutionError('Script %s (%s) ViriScript class does'
                ' not implement a run method' % (original_filename, script_id))

    def execute(self, script_id):
        """Executes the specified script. The script must contain a class
        named ViriScript, which implements a run method, containing the entry
        point for all the script functionality. This way, we're able to add
        some attributes to the class with host specific information.

        Example script, returning if data directory has already been created
        (note that the data_dir attribute is not defined on the class, but is
        added on execution time through the context):

        >>> import os
        >>>
        >>> class ViriScript:
        >>>     def run(self):
        >>>         return os.path.isdir(self.data_dir)

        Arguments:
        script_id -- identifier (hash) of the script to execute
        """
        script_cls = self._load_script(script_id)
        base_id = Base.get()
        if base_id:
            base_cls = self._load_script(base_id)
            parents = (script_cls, base_cls)
        else:
            parents = (script_cls,)

        # TODO add access to data files
        cls = type('ExecScript', parents, dict(data=lambda x: x))
        try:
            res = cls().run()
            success = True
        except Exception as exc:
            res = exc
            success = False

        Execution.create(
            script_id=script_id,
            success=success,
            result=res)

        if not success:
            (exc_type, exc_val, exc_tb) = sys.exc_info()
            res = '%s\n%s' % ('\n'.join(traceback.format_tb(exc_tb)), exc_val)
            raise self.ExecutionError('Script execution failed:\n%s' %
                res)

        return res

