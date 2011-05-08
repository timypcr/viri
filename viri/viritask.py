import os
import datetime
from hashlib import sha1

BASE_TASK = '__base__'

class Task:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def save(self, task_filename, task_binary):
        """Receives a source file and stores it in the scripts
        directory. To do so, a hash of the script content is
        calculated and used as the file name.
        This way we will only need to send scripts which are
        not yet on the remote host, and we'll handle versioning
        of the scripts in a reliable way.

        Script is threated as binary, so .pyc and .pyo files
        can be used.

        Arguments:
        task_filename -- original file name
        task_binary -- content of the task processed usgin
            xmlrpc.client.Binary.encode()
        """
        file_type = task_filename.split('.')[-1]
        task_id = sha1(task_binary.data).hexdigest()
        base_dst = os.path.join(self.task_dir, task_id)
        dst_file = '%s.%s' % (base_dst, file_type)
        if not os.path.isfile(dst_file):
            with open(dst_file, 'wb') as task_file:
                task_file.write(task_binary.data)
                with open('%s.info' % base_dst, 'a') as info_file:
                    info_file.write('%s %s' % (datetime.datetime.now(),
                        task_filename))
        return task_id
    
    def execute(self, script_hash):
        """Executes the specified script. The script must
        contain a class named ViriTask, which implements
        a run method, containing the entry point for all
        the script functionality.
        This way, we're able to add some attributes to the
        class with host specific information.

        Example script, returning if data directory has
        already been created (note that the data_dir
        attribute is not defined on the class, but is
        added on execution time):
        >>> import os
        >>>
        >>> class ViriTask:
        >>>     def run(self):
        >>>         return os.path.isdir(self.data_dir)

        Arguments:
        script_hash -- sha1 hash of the code to execute,
            this hash is the one returned by send_script
            function
        """
        parent_classes = (__import__(script_hash).ViriTask,)
        try:
            parent_classes += (__import__(BASE_TASK).ViriTask,)
        except ImportError:
            pass
        extra_attrs = dict(data_dir=self.data_dir)
        return type('ExecTask', parent_classes, extra_attrs)().run()

