import logging
import traceback
import socket
import socketserver
import ssl
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, \
    SimpleXMLRPCRequestHandler
from viri.objects import Script, DataFile, Execution


RPC_METHODS = ('execute', 'put', 'ls', 'get', 'history')
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
            ssl_version=PROTOCOL)
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
            res = traceback.format_exc()
            logging.error(res)
            return (ERROR, res)
        else:
            return res
    return inner


class RPCServer:
    """XML-RPC server, implementing the main functionality of the application.
    """
    def __init__(self, port, ca_file, cert_key_file, db, context):
        """Saves arguments as class attributes and prepares
        task and data directories
        
        Arguments:
        port -- port number where server will be listening
        ca_file -- Recognized CA certificates
        cert_key_file -- File with daemon's certificate and private key,
            for TLS negotiation
        db - viri database handler
        context - functions and data that will be made available on viri
            scripts. This is custom settings, Script, DataFile, Execution
            objects and the viri db
        """
        self.port = port
        self.ca_file = ca_file
        self.cert_key_file = cert_key_file
        self.db = db
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

    @public
    def execute(self, filename_or_id):
        """Executes a script and returns the script id and the execution
        result, which can be the return of the script in case of success
        or the traceback and error message in case of failure.
        It is possible to execute a script already sent, given its id, or
        to send the script to execute, using the original script file name
        and the script (file) content.
        """
        try:
            res = Script.execute(self.db, filename_or_id)
        except:
            res = traceback.format_exc()
            return (ERROR, res)
        else:
            return (SUCCESS, res)

    @public
    def put(self, file_name, file_content, data=False):
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
        """
        if data:
            DataFile.create(self.db,
                dict(filename=file_name, content=file_content.data))
            return (SUCCESS, 'Data file %s successfully saved' % file_name)
        else:
            script_id = Script.create(self.db,
                dict(filename=file_name, content=file_content.data)
                ).script_id
            return (SUCCESS, script_id)

    @public
    def ls(self, data=False):
        """List scripts or files in the data directory"""
        if data:
            return (SUCCESS, str(
                DataFile.query(self.db,
                    fields=('filename', 'saved'),
                    order=('filename', 'saved'))))
        else:
            return (SUCCESS, str(
                Script.query(self.db,
                    fields=('filename', 'script_id', 'saved'),
                    order=('filename', 'saved'))))

    @public
    def get(self, filename_or_id, data=False):
        """Returns the content of a file"""
        res = (DataFile if data else Script).get_content(
            self.db, filename_or_id)

        if res:
            return (SUCCESS, xmlrpc.client.Binary(res.content))
        else:
            return (ERROR, 'File {} not found'.format(filename_or_id))

    @public
    def history(self):
        return (SUCCESS, str(
            Execution.query(self.db,
                fields=('executed', 'filename', 'script_id', 'success'),
                order=('executed',))))

