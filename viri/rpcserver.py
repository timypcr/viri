import sys
import os
import logging
import traceback
import socket
import socketserver
import ssl
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, \
    SimpleXMLRPCRequestHandler
from viri.viritask import Task

PROTOCOL = ssl.PROTOCOL_TLSv1
SUCCESS = 0
ERROR = 1

RPC_METHODS = ('send_data',
    'send_task',
    'exec_task')


class SimpleXMLRPCServerTLS(SimpleXMLRPCServer):
    """Overriding standard xmlrpc.server.SimpleXMLRPCServer to run over TLS.
    Changes inspired by
    http://www.cs.technion.ac.il/~danken/SecureXMLRPCServer.py
    """
    def __init__(self, addr, ca_file, cert_key_file,
        requestHandler=SimpleXMLRPCRequestHandler, logRequests=True,
        allow_none=False, encoding=None, bind_and_activate=True):
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
            certfile=cert_key_file,
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
    send_data -- Receives a data file from the client and saves it in
        data_dir directory
    send_task -- Receives a Python source file from the client, calculates a
        hash for it, and saves it in the task_dir using the hash as its name
    exec_task -- executes a task previously send, given its id (hash)
    """
    def __init__(self, port, ca_file, cert_key_file, data_dir, task_dir):
        """Saves arguments as class attributes and prepares
        task and data directories
        
        Arguments:
        port -- port number where server will be listening
        ca_file -- Recognized CA certificates
        cert_key_file -- File with daemon's certificate and private key,
            for TLS negotiation
        data_dir -- directory to store non-code sent files
        task_dir -- directory to store python code representing tasks
        """
        self.port = port
        self.ca_file = ca_file
        self.cert_key_file = cert_key_file
        self.data_dir = data_dir
        self.task_dir = task_dir

    def start(self):
        """Starts the XML-RPC server, and registers all public methods."""
        server = SimpleXMLRPCServerTLS(
            ('', self.port),
            ca_file=self.ca_file,
            cert_key_file=self.cert_key_file,
            logRequests=False)
        for method in RPC_METHODS:
            server.register_function(getattr(self, method))
        server.serve_forever()

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

    def send_task(self, task_filename, task_binary):
        """Receives a source file and stores it in the tasks directory.
        To do so, a hash of the task content is calculated and used as the
        file name. This way we will only need to send tasks which are not
        yet on the remote host, and we'll handle versioning of the tasks in
        a reliable way.

        Script is threated as binary, so .pyc and .pyo files can be used.

        Arguments:
            task_filename -- original file name
            task_binary -- content of the task processed using
                xmlrpc.client.Binary.encode()
        """
        try:
            task = Task(self.data_dir)
            task_id = task.save(task_filename, task_binary)
            return '%s %s' % (SUCCESS, task_id)
        except Exception as exc:
            logging.error('Unable to save task file %s: %s' % (
                task_filename, str(exc)))
            return self._get_error()

    def exec_task(self, task_id):
        try:
            task = Task(self.data_dir)
            result = task.execute(task_id)
            logging.info('Task %s succesfully executed' % task_id) # FIXME log name, not id
            return '%s %s' % (SUCCESS, result)
        except Exception as exc:
            logging.warning('Task %s failed: %s' % (
                task_id,
                str(exc)))
            return self._get_error()

