import sys
import os
import logging
import datetime
import traceback
import socket
import socketserver
import ssl
import xmlrpc.client
from hashlib import sha1
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, \
    SimpleXMLRPCRequestHandler
from viri.viritask import TaskExecutor

PROTOCOL = ssl.PROTOCOL_TLSv1
SUCCESS = 0
ERROR = 1

RPC_METHODS = ('put', 'get', 'ls', 'mv', 'execute')


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


def public(func):
    """Decorator that controls arguments of public methods. XMLRPC only
    works with positional arguments, so the client always sends only one
    parameter with a dictionary. This decorator executes the method
    passing the items in the dictionary as keyword arguments.
    """
    def inner(self, kwargs):
        return func(self, **kwargs)
    return inner


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
    def __init__(self, port, ca_file, cert_key_file,
        data_dir, script_dir, context):
        """Saves arguments as class attributes and prepares
        task and data directories
        
        Arguments:
        port -- port number where server will be listening
        ca_file -- Recognized CA certificates
        cert_key_file -- File with daemon's certificate and private key,
            for TLS negotiation
        data_dir -- directory to store non-code sent files
        task_dir -- directory to store python code representing tasks
        custom_settings -- dictionary containing configuration directives
            which will be available on `conf' attribute of tasks
        """
        self.port = port
        self.ca_file = ca_file
        self.cert_key_file = cert_key_file
        self.data_dir = data_dir
        self.script_dir = script_dir
        self.context = context

    def start(self):
        """Starts the XML-RPC server, and registers all public methods."""
        server = SimpleXMLRPCServerTLS(
            ('', self.port),
            ca_file=self.ca_file,
            cert_key_file=self.cert_key_file,
            logRequests=False)
        for method in RPC_METHODS:
            server.register_function(getattr(self, method), method)
        server.serve_forever()

    def _get_error(self):
        """Captures the error and the traceback, and formats
        them to be sent to the client.
        """
        (exc_type, exc_val, exc_tb) = sys.exc_info()
        tb = '\n'.join(traceback.format_tb(exc_tb))
        return (ERROR, '%s\n%s' % (tb, str(exc_val)))

    def _save_script(self, filename, content):
        """Receives a source file and stores it in the scripts directory. To
        do so, a hash of the script content is calculated and used as the file
        name. This way we will only need to send scripts which are not yet on
        the remote host, and we'll handle versioning of the scripts in a
        reliable way.

        Script is threated as binary, so .pyc and .pyo files can be used.

        Arguments:
        task_filename -- original file name
        task_binary -- content of the task processed using
            xmlrpc.client.Binary.encode()
        """
        file_type = filename.split('.')[-1]
        script_id = sha1(content.data).hexdigest()
        base_dst = os.path.join(self.script_dir, script_id)
        dst_file = '%s.%s' % (base_dst, file_type)
        if not os.path.isfile(dst_file):
            with open(dst_file, 'wb') as task_file:
                task_file.write(content.data)
                with open('%s.info' % base_dst, 'a') as info_file:
                    info_file.write('%s %s' % (datetime.datetime.now(),
                        filename))
        return script_id

    @public
    def execute(self, script_id):
        """Executes a script
        """
        try:
            task = TaskExecutor(self.context)
            result = task.execute(script_id)
            logging.info('Script %s succesfully executed' % script_id) # FIXME log name, not id
            return (SUCCESS, result)
        except Exception as exc:
            logging.warning('Script %s execution failed: %s' % (
                script_id, str(exc)))
            return self._get_error()

    @public
    def put(self, filename, content, data=False, overwrite=False):
        """Receives a data file from the remote instance, and copies it to the
        data directory.

        Arguments:
        filename -- original file name
        content -- content of the file processed using
            xmlrpc.client.Binary.encode()
        overwrite -- specifies if file should be overwritten in case a file
            with same name exists
        """
        try:
            if not data:
                script_id = self._save_script(filename, content)
                return (SUCCESS, script_id)
            else:
                filename = os.path.join(self.data_dir, filename)
                if not os.path.isfile(filename) or overwrite:
                    with open(filename, 'wb') as f:
                        f.write(content.data)
                    msg = 'Data file %s saved' % filename
                    logging.info(msg)
                    return (SUCCESS, msg)
                else:
                    msg = 'Not overwriting file %s' % filename
                    logging.debug(msg)
                    return (SUCCESS, msg)
        except Exception as exc:
            logging.error('Error saving file %s: %s' % (
                filename,
                str(exc)))
            return self._get_error()

    @public
    def ls(self, data=False):
        """List the files in the data directory"""
        if data:
            return (SUCCESS, '\n'.join(os.listdir(self.data_dir)))
        else:
            return (SUCCESS, '\n'.join(os.listdir(self.script_dir)))

    @public
    def get(self, filename):
        """Returns the content of a file"""
        full_filename = os.path.join(self.data_dir, filename)
        if os.path.split(full_filename) == full_filename:
            if os.path.isfile(full_filename):
                with open(full_filename, 'r') as f:
                    return (SUCCESS, xmlrpc.client.Binary(f.read()))
            else:
                return (ERROR, 'File does not exist')
        else:
            return (ERROR, 'No paths allowed on file names')

    @public
    def mv(self, src, dst):
        """Renames a file in the data directory"""
        if src == os.path.split(src) and dst == os.path.split(dst):
            if os.path.isfile(os.path.join(self.data_dir, src)):
                os.rename(
                    os.path.join(self.data_dir, src),
                    os.path.join(self.data_dir, dst))
            else:
                return (ERROR, 'File does not exist')
        else:
            return (ERROR, 'No paths allowed on file names')

