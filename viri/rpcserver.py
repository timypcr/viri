import sys
import os
import traceback
from xmlrpc.server import SimpleXMLRPCServer
from hashlib import sha1

class RPCServer:
    def __init__(self, port, task_dir):
        self.port = port
        self.task_dir = task_dir
        self._prepare_task_dir()

        server = SimpleXMLRPCServer(('', port), logRequests=False)
        server.register_function(self.execute)
        server.serve_forever()

    def _prepare_task_dir(self):
        if not os.path.isdir(self.task_dir):
            os.mkdir(self.task_dir)

        init_filename = os.path.join(self.task_dir, '__init__.py')
        if not os.path.isfile(init_filename):
            open(init_filename, 'w').close()

        abs_task_dir = os.path.abspath(self.task_dir)
        if abs_task_dir not in sys.path:
            sys.path.append(abs_task_dir)

    def execute(self, src, signature):
        src_id = sha1(src.encode('utf-8')).hexdigest()
        dst_filename = '.'.join((os.path.join(self.task_dir, src_id), 'py'))
        if not os.path.isfile(dst_filename):
            f = open(dst_filename, 'w')
            f.write(src)
            f.close()
        try:
            __import__(src_id)
        except:
            (exc_type, exc_val, exc_tb) = sys.exc_info()
            return '\n'.join(traceback.format_tb(exc_tb)[1:] + [str(exc_val)])
        else:
            return 0

