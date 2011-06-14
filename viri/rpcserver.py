import sys
import os
import logging
import traceback
import socket
import socketserver
import ssl
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, \
    SimpleXMLRPCRequestHandler

RPC_METHODS = ('execute', 'put', 'ls', 'get', 'history', 'mv', 'rm')
PROTOCOL = ssl.PROTOCOL_TLSv1
SUCCESS = 0
ERROR = 1


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
    It also captures any error non-controlled error, logs it, and sends
    it to the client as text.
    """
    def inner(self, kwargs):
        try:
            res = func(self, **kwargs)
        except:
            (exc_type, exc_val, exc_tb) = sys.exc_info()
            tb = '\n'.join(traceback.format_tb(exc_tb))
            res = '%s\n%s' % (tb, str(exc_val))
            logging.error(res)
            return (ERROR, res)
        else:
            return res
    return inner


def protect(directory, filename):
    """Returns the absolute path to the file in the directory, only if the
    filename is in the directory. This is done to prevent access to files
    outside the Viri working directory, if the user sends as a parameter
    something like ../../../etc/passwd
    """
    req_path = os.path.abspath(os.path.normpath(os.path.join(
        directory, filename)))
    allowed_path = os.path.abspath(os.path.normpath(os.path.join(
        directory, os.path.basename(filename))))
    if req_path == allowed_path:
        return req_path
    else:
        return None


class RPCServer:
    """XML-RPC server, implementing the main functionality of the application.
    """
    def __init__(self, port, ca_file, cert_key_file,
        script_dir, data_dir, script_manager):
        """Saves arguments as class attributes and prepares
        task and data directories
        
        Arguments:
        port -- port number where server will be listening
        ca_file -- Recognized CA certificates
        cert_key_file -- File with daemon's certificate and private key,
            for TLS negotiation
        script_dir -- directory to store python code representing tasks
        data_dir -- directory to store non-code sent files
        script_manager -- ScriptManager instance used to handle script
            operations
        """
        self.port = port
        self.ca_file = ca_file
        self.cert_key_file = cert_key_file
        self.script_dir = script_dir
        self.data_dir = data_dir
        self.script_manager = script_manager

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

    @public
    def execute(self, script_id=None, file_name=None, file_content=None,
        use_id=False):
        """Executes a script and returns the script id and the execution
        result, which can be the return of the script in case of success
        or the traceback and error message in case of failure.
        It is possible to execute a script already sent, given its id, or
        to send the script to execute, using the original script file name
        and the script (file) content.

        Arguments:
        script_id -- the script sha1 hash, used as script identifier
        file_name -- the original script file name
        file_content -- the script content (code)
        use_id -- specifies if the script id, or both the file name and
            content are sent to request the script execution
        """
        if not use_id:
            script_id = self.script_manager.save_script(
                file_name, file_content.data)

        try:
            result = self.script_manager.execute(script_id)
        except self.script_manager.ExecutionError as exc:
            return (ERROR, '%s %s' % (script_id, exc))

        else:
            return (SUCCESS, '%s %s' % (script_id, result))

    @public
    def put(self, file_name, file_content, data=False, overwrite=False):
        """Receives a script or a data file from viric, and saves it in the
        local filesystem.
        Scripts are saved using it's id as file name, and info about them is
        saved in an info file, which keeps the original name.
        Data files are saved as they are keeping the name.

        Arguments:
        file_name -- original file name
        file_content -- content of the file processed using
            xmlrpc.client.Binary.encode()
        data -- specifies that sent file is a data file and not a script
        overwrite -- specifies if file should be overwritten in case a file
            with same name exists
        """
        if not data:
            script_id = self.script_manager.save_script(
                file_name, file_content.data)

            return (SUCCESS, script_id)
        else:
            filename = os.path.join(self.data_dir, file_name)
            exists = os.path.isfile(filename)
            if not exists or overwrite:
                with open(filename, 'wb') as f:
                    f.write(file_content.data)
                if exists:
                    msg = 'Data file %s overwrote' % file_name
                else:
                    msg = 'Data file %s saved' % file_name
                logging.info(msg)
                return (SUCCESS, msg)
            else:
                msg = 'Not overwriting file %s' % file_name
                logging.debug(msg)
                return (SUCCESS, msg)

    @public
    def ls(self, data=False, verbose=False):
        """List scripts or files in the data directory"""
        if not data:
            return (SUCCESS, '\n'.join(self.script_manager.list(verbose)))
        else:
            return (SUCCESS, '\n'.join(os.listdir(self.data_dir)))

    @public
    def get(self, filename_or_id, use_id=False, data=False):
        """Returns the content of a file"""
        if not data:
            if use_id:
                script_id = filename_or_id
            else:
                script_id = self.script_manager.id_by_name(filename_or_id)
            filename = self.script_manager.filename_by_id(script_id)
        else:
            filename = protect(self.data_dir, filename_or_id)
        if filename:
            if os.path.isfile(filename):
                with open(filename, 'rb') as f:
                    return (SUCCESS, xmlrpc.client.Binary(f.read()))
            else:
                return (ERROR, 'File does not exist')
        else:
            return (ERROR, 'File not found.'
                ' File names cannot include directories')

    @public
    def history(self):
        return (SUCCESS, self.script_manager.history())

    @public
    def mv(self, source, destination, overwrite=False):
        """Renames a file in the data directory"""
        source_path = protect(self.data_dir, source)
        destination_path = protect(self.data_dir, destination)
        if source_path and destination_path:
            if os.path.isfile(source_path):
                dst_exists = os.path.isfile(destination_path)
                if not dst_exists or overwrite == True:
                    os.rename(source_path, destination_path)
                if not dst_exists:
                    return (SUCCESS, 'File %s successfully renamed to %s' % (
                        source, destination))
                elif overwrite == True:
                    return (SUCCESS, 'Existing file %s replaced'
                    ' by renaming %s' % (destination, source))
                else:
                    return (ERROR, 'Rename aborted because destination file'
                        ' already exists. Use --overwrite to force it')
            else:
                return (ERROR, 'File %s not found' % source)
        else:
            return (ERROR, 'File names cannot include directories')

    @public
    def rm(self, filename):
        path = protect(self.data_dir, filename)
        if path and os.path.isfile(path):
            os.remove(path)
            return (SUCCESS, 'File %s successfully removed' % filename)
        else:
            return (ERROR, 'File not found.'
                ' File names cannot include directories')

