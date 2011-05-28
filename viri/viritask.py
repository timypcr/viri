import logging

BASE_TASK = '__base__'

class TaskExecutor:
    def __init__(self, context):
        """Initializes the executor, setting a context which will be made
        available in the tasks.

        Arguments:
        context -- a dictionary that will be made available on
            tasks, making every key an attribute of the task instance
        """
        self.context = context

    def execute(self, script_id):
        """Executes the specified script. The script must contain a class
        named ViriTask, which implements a run method, containing the entry
        point for all the script functionality. This way, we're able to add
        some attributes to the class with host specific information.

        Example script, returning if data directory has already been created
        (note that the data_dir attribute is not defined on the class, but is
        added on execution time through the context):

        >>> import os
        >>>
        >>> class ViriTask:
        >>>     def run(self):
        >>>         return os.path.isdir(self.data_dir)

        Arguments:
        script_id -- sha1 hash of the code to execute, this hash is the one
        returned by send_script function
        """
        parent_classes = (__import__(script_id).ViriTask,)
        try:
            parent_classes += (__import__(BASE_TASK).ViriTask,)
        except ImportError:
            logging.debug('Base task not found for script %s' % script_id)

        logging.info('Executing script with id %s' % script_id)
        return type('ExecTask', parent_classes, self.context)().run()

