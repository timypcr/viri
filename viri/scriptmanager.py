import os
import datetime
import logging
import glob
import json
from hashlib import sha1

BASE_SCRIPT = '__base__'
HISTORY_FILE = 'history'
NAMES_FILE = 'names.json'

class ScriptManager:
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

    def id_by_name(self, script_name):
        """Returns the id of the last version of a script given its name"""
        with open(os.path.join(self.info_dir), 'r') as f:
            # there are more efficient ways to get the last line, but we
            # expect very small files, so it's worthless to implement them
            return f.readlines()[-1].split(' ')[0]

    def name_by_id(self, script_id):
        """Returns the name of a script given its id"""
        name_map = json.load(self.names_file)
        return name_map.get(script_id)

    def save_script(self, filename, content):
        """Saves the script in the scripts directory, adds its id to the
        information file of its file name, and adds the id and name to the
        names dictionary.

        Arguments:
        filename -- original script file name
        content -- script content (code)
        """
        file_type = filename.rsplit('.')[-1]
        script_id = sha1(content).hexdigest()

        script_path = os.path.join(self.script_dir,
            '%s.%s' % (script_id, file_type))
        with open(script_path, 'wb') as script_file:
            script_file.write(content)

        info_path = os.path.join(self.info_dir,
            '%s.info' % filename)
        with open(info_path, 'a') as info_file:
            info_file.write('%s %s' % (script_id, datetime.datetime.now()))

        name_map = json.load(self.names_file)
        name_map[script_id] = filename
        json.dump(name_map, self.names_file)

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
        parent_classes = (__import__(script_id).ViriScript,)
        try:
            parent_classes += (__import__(BASE_SCRIPT).ViriScript,)
        except ImportError:
            logging.debug('Base script not found for script %s' % script_id)

        logging.info('Executing script %s/%s' % (self.script_name, script_id))
        with open(self.history_file, 'a') as f:
            f.write('%s %s %s\n' % (datetime.datetime.now(),
                self.script_id, self.script_name))
        return type('ExecScript', parent_classes, self.context)().run()

    def list(self, verbose=False):
        """List all installed scripts"""
        # TODO verbose
        res = []
        for filename in glob.glob(os.path.join(self.info_dir, '*.info')):
            res.append(os.path.basename(filename).rstrip('.info'))

        return res

