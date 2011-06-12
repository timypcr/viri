import sys
import os
import datetime
import logging
import traceback
import glob
import json
from hashlib import sha1

BASE_SCRIPT = '__base__'
HISTORY_FILE = 'history'
NAMES_FILE = 'names.json'


class ScriptManager:
    class ExecutionError(Exception):
        """Represents any error during script execution"""
        pass

    def __init__(self, script_dir, info_dir, context):
        """Sets class attributes

        Arguments:
        script_dir -- directory where scripts are stored
        info_dir -- directory where information about scripts is stored
        context -- dictionary containing values that will be available
            as attributes of the ViriScript class in the script
        """
        self.script_dir = script_dir
        self.info_dir = info_dir
        self.context = context
        self.history_file = os.path.join(info_dir, HISTORY_FILE)
        self.names_file = os.path.join(self.info_dir, NAMES_FILE)

    def _get_name_map(self):
        # TODO check if data is corrupted and regenerate the whole file
        if os.path.isfile(self.names_file):
            with open(self.names_file, 'r') as f:
                return json.load(f)
        else:
            return {}

    def id_by_name(self, script_name):
        """Returns the id of the last version of a script given its name"""
        info_filename = os.path.join(self.info_dir, '%s.info' % script_name)
        if os.path.isfile(info_filename):
            with open(info_filename, 'r') as f:
                # there are more efficient ways to get the last line, but we
                # expect very small files, so it's worthless to implement them
                return f.readlines()[-1].split(' ')[0]
        else:
            return None

    def name_by_id(self, script_id):
        """Returns the name of a script given its id"""
        return self._get_name_map().get(script_id)

    def filename_by_id(self, script_id):
        """Returns the absolute path of a script given its id"""
        script_name = self.name_by_id(script_id)
        if script_name:
            ext = os.path.splitext(script_name)[-1]
            return os.path.join(self.script_dir, '%s.%s' % (script_id, ext))
        else:
            return None

    def save_script(self, filename, content):
        """Saves the script in the scripts directory, adds its id to the
        information file of its file name, and adds the id and name to the
        names dictionary.

        Arguments:
        filename -- original script file name
        content -- script content (code)
        """
        ext = os.path.splitext(filename)[-1]
        script_id = sha1(content).hexdigest()

        script_path = os.path.join(self.script_dir,
            '%s.%s' % (script_id, ext))
        with open(script_path, 'wb') as script_file:
            script_file.write(content)

        info_path = os.path.join(self.info_dir,
            '%s.info' % filename)
        with open(info_path, 'a') as info_file:
            info_file.write('%s %s' % (script_id, datetime.datetime.now()))

        name_map = self._get_name_map()
        name_map[script_id] = filename
        with open(self.names_file, 'w') as f:
            json.dump(name_map, f)

        return script_id

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
        context -- extra information that will be made available on attributes
            of the ViriScript on the script
        """
        try:
            script_mod = __import__(script_id)
        except ImportError as exc:
            raise self.ExecutionError('Cannot import script %s: %s' % (
                script_id, exc))

        if not hasattr(script_mod, 'ViriScript'):
            raise self.ExecutionError('Script %s does not implement'
                ' a ViriScript class' % script_id)

        parent_classes = (script_mod.ViriScript,)

        try:
            base_mod = __import__(BASE_SCRIPT)
        except ImportError:
            logging.debug('Base script not found for script %s' % script_id)
        else:
            if not hasattr(base_mod, 'ViriScript'):
                raise self.ExecutionError('Base script does not implement'
                    ' a ViriScript class')
            else:
                parent_classes += (base_mod.ViriScript,)

        logging.info('Executing script %s' % script_id)

        cls = type('ExecScript', parent_classes, self.context)

        try:
            res = cls().run()
            success = True
        except Exception as exc:
            success = False
            res = exc

        with open(self.history_file, 'a') as f:
            f.write('%s\n' % '\t'.join((
                datetime.datetime.now(),
                self.script_id,
                self.script_name,
                'SUCCESS' if success else 'ERROR',
                res)))

        if not success:
            (exc_type, exc_val, exc_tb) = sys.exc_info()
            tb = '\n'.join(traceback.format_tb(exc_tb))
            res = '%s\n%s' % (tb, str(exc_val))
            raise self.ExecutionError('Script execution failed:\n%s' %
                res)

        return res

    def list(self, verbose=False):
        """List all installed scripts"""
        # TODO verbose
        res = []
        for filename in glob.glob(os.path.join(self.info_dir, '*.info')):
            res.append(os.path.basename(filename).rstrip('.info'))

        return res

    def history(self):
        if os.path.isfile(self.history_file):
            with open(self.history_file, 'r') as f:
                return f.read()
        else:
            return ''
