import sys
import os
import datetime
import logging
import traceback
import socket
import socketserver
import ssl
from hashlib import sha1
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, SimpleXMLRPCRequestHandler

PROTOCOL = ssl.PROTOCOL_TLSv1
SUCCESS = 0
ERROR = 1

RPC_METHODS = (
    'send_data',
    'send_task',
    'exec_task')


"""Overriding standard xmlrpc.server.SimpleXMLRPCServer to run over TLS
Changes inspired on http://www.cs.technion.ac.il/~danken/SecureXMLRPCServer.py
"""
class SimpleXMLRPCServerTLS(SimpleXMLRPCServer):
    def __init__(self, addr, ca_file, requestHandler=SimpleXMLRPCRequestHandler,
                 logRequests=True, allow_none=False, encoding=None, bind_and_activate=True):
        """Overriding __init__ method of the SimpleXMLRPCServer

        The method is a copy, except for the TCPServer __init__
        call, which is rewritten using TLS, and the certfile argument
        which is required for TLS
        """
        self.logRequests = logRequests
        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding)
        socketserver.BaseServer.__init__(self, addr, requestHandler)
        self.socket = ssl.wrap_socket(
            socket.socket(self.address_family, self.socket_type),
            server_side=True,
            certfile='keys/virid.pem', # FIXME set as an argument
            ca_certs=ca_file,
            cert_reqs=ssl.CERT_REQUIRED,
            ssl_version=PROTOCOL,
            )
        if bind_and_activate:
            self.server_bind()
            self.server_activate()

        # [Bug #1222790] If possible, set close-on-exec flag; if a
        # method spawns a subprocess, the subprocess shouldn't have
        # the listening socket open.
        try:
            import fcntl
        except ImportError:
            pass
        else:
            if hasattr(fcntl, 'FD_CLOEXEC'):
                flags = fcntl.fcntl(self.fileno(), fcntl.F_GETFD)
                flags |= fcntl.FD_CLOEXEC
                fcntl.fcntl(self.fileno(), fcntl.F_SETFD, flags)


class RPCServer:
    """XML-RPC server, implementing the main functionality of the
    application.

    Public methods:
    send_data -- Receives a data file from the client and
        saves it in data_dir directory
    send_script -- Receives a Python source file from the
        client, calculates a hash for it, and saves it
        in the task_dir using the hash as its name
    exec -- executes a task previously send, given its hash
    """
    def __init__(self, port, ca_file, task_dir, data_dir, log_requests):
        """Saves arguments as class attributes and prepares
        task and data directories
        
        Arguments:
        port -- port number where server will be listening
        cert_file -- Recognized CA certificates
        task_dir -- directory where tasks will be stored
        data_dir -- directory where data files will be stored
        log_requests -- boolean specifying if requests have
            to be recorded in the log
        """
        self.port = port
        self.ca_file = ca_file
        self.task_dir = task_dir
        self.data_dir = data_dir
        self.log_requests = log_requests
        self._prepare_dirs()

    def start(self):
        """Starts the XML-RPC server, and registers all public
        methods.
        """
        server = SimpleXMLRPCServerTLS(
            ('', self.port),
            ca_file=self.ca_file,
            logRequests=self.log_requests)
        for method in RPC_METHODS:
            server.register_function(getattr(self, method))
        server.serve_forever()

    def _prepare_dirs(self):
        """Creates the directories for storing scripts
        and data, in case they doesn't exist. Also
        creates an empty __init__.py file in scripts
        directory, so scripts can be imported.
        """
        if not os.path.isdir(self.task_dir):
            os.mkdir(self.task_dir)

        init_filename = os.path.join(self.task_dir, '__init__.py')
        if not os.path.isfile(init_filename):
            open(init_filename, 'w').close()

        abs_task_dir = os.path.abspath(self.task_dir)
        if abs_task_dir not in sys.path:
            sys.path.append(abs_task_dir)

        if not os.path.isdir(self.data_dir):
            os.mkdir(self.data_dir)

    def _get_error(self):
        """Captures the error and the traceback, and formats
        them to be sent to the client.
        """
        (exc_type, exc_val, exc_tb) = sys.exc_info()
        tb = '\n'.join(traceback.format_tb(exc_tb))
        return '%s %s\n%s' % (ERROR, tb, str(exc_val))

    def send_data(self, data_filename, data_binary, overwrite=False):
        """Receives a data file from the remote instance,
        and copies it to the data directory.

        Arguments:
        data_filename -- original file name
        data_binary -- content of the file processed using
            xmlrpc.client.Binary.encode()
        overwrite -- specifies if overwrite in case a file with
            same name exists
        """
        try:
            filename = os.path.join(self.data_dir, data_filename)
            if not os.path.isfile(filename) or overwrite:
                with open(filename, 'wb') as f:
                    f.write(data_binary.data)
                msg = 'Data file %s saved' % data_filename
                logging.info(msg)
                return '%s %s' % (SUCCESS, msg)
            else:
                msg = 'Not overwriting file %s' % data_filename
                logging.debug(msg)
                return '%s %s' % (SUCCESS, msg)
        except Exception as exc:
            logging.error('Unable to save data file %s: %s' % (
                data_filename,
                str(exc)))
            return self._get_error()

    def send_task(self, script_filename, script_binary):
        """Receives a source file and stores it in the scripts
        directory. To do so, a hash of the script content is
        calculated and used as the file name.
        This way we will only need to send scripts which are
        not yet on the remote host, and we'll handle versioning
        of the scripts in a reliable way.

        Script is threated as binary, so .pyc and .pyo files
        can be used.

        Arguments:
        script_filename -- original file name
        script_binary -- content of the script processed usgin
            xmlrpc.client.Binary.encode()
        """
        try:
            file_type = script_filename.split('.')[-1]
            script_hash = sha1(script_binary.data).hexdigest()
            base_dst = os.path.join(self.task_dir, script_hash)
            dst_script = '%s.%s' % (base_dst, file_type)
            if not os.path.isfile(dst_script):
                with open(dst_script, 'wb') as script_file:
                    script_file.write(script_binary.data)
                    with open('%s.info' % base_dst, 'w') as info_file:
                        info_file.write(script_filename),
                        info_file.write(str(datetime.datetime.now()))
            return '%s %s' % (SUCCESS, script_hash)
        except Exception as exc:
            logging.error('Unable to save script file %s: %s' % (
                script_filename, str(exc)))
            return self._get_error()

    def exec_task(self, script_hash):
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
        try:
            mod = __import__(script_hash)
            extra_attrs = dict(data_dir=self.data_dir)
            result = type('ExecTask', (mod.ViriTask,), extra_attrs)().run()
            logging.info('Task %s succesfully executed' % script_hash)
            return '%s %s' % (SUCCESS, result)
        except Exception as exc:
            logging.warning('Task %s failed: %s' % (
                script_hash,
                str(exc)))
            return self._get_error()

