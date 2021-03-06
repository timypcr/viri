# Copyright 2011, Marc Garcia <garcia.marc@gmail.com>
#
# This file is part of Viri.
#
# Viri is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Viri is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Viri.  If not, see <http://www.gnu.org/licenses/>.

from libviri.virirpc import XMLRPCServer


RPC_METHODS = ['execute', 'put', 'get', 'ls', 'mv', 'rm', 'exists', 'version']
SUCCESS = True
ERROR = False


def public(func):
    """Decorator that controls arguments of public methods. XMLRPC only
    works with positional arguments, so the client always sends only one
    parameter with a dictionary. This decorator executes the method
    passing the items in the dictionary as keyword arguments.
    It also captures any error non-controlled error, logs it, and sends
    it to the client as text.
    """
    import logging
    import traceback

    def inner(self, kwargs, cert):
        try:
            res = func(self, cert, **kwargs)
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
    def __init__(self, port, ca_file, cert_key_file, db, context, crl_file_url):
        """Saves arguments as class attributes and prepares
        task and data directories
        
        Arguments:
        port -- port number where server will be listening
        ca_file -- Recognized CA certificates
        cert_key_file -- File with daemon's certificate and private key,
            for TLS negotiation
        db - viri database handler
        context - functions and data that will be made available on viri
            scripts. This is custom settings, Script, DataFile objects and the
            viri db
        crl_file_url - URL of a certificate revocation list (CRL)
        """
        self.port = port
        self.ca_file = ca_file
        self.cert_key_file = cert_key_file
        self.db = db
        self.context = context
        self.crl_file_url = crl_file_url

    def start(self):
        """Starts the XML-RPC server, and registers all public methods."""
        self.server = XMLRPCServer(
            ('', self.port),
            ca_file=self.ca_file,
            cert_key_file=self.cert_key_file,
            logRequests=False,
            allow_none=True,
            crl_file_url=self.crl_file_url)
        for method in RPC_METHODS:
            self.server.register_function(getattr(self, method), method)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()

    @public
    def execute(self, cert, file_name_or_id, args):
        """Executes a script and returns the script id and the execution
        result, which can be the return of the script in case of success
        or the traceback and error message in case of failure.
        It is possible to execute a script already sent, given its id, or
        to send the script to execute, using the original script file name
        and the script (file) content.
        """
        import traceback
        from libviri.objects import File

        try:
            success, res = File.execute(self.db, file_name_or_id,
                args, self.context, cert)
        except File.Missing:
            return (ERROR, 'File not found')
        except:
            return (ERROR, traceback.format_exc())
        else:
            return (SUCCESS if success else ERROR, res)

    @public
    def put(self, cert, file_name, file_content):
        """Receives a script or a data file from viric, and saves it in the
        viri database. A content hash is used as id, so if the file exists,
        it's not saved again.

        Arguments:
        file_name -- original file name
        file_content -- content of the file processed using
            xmlrpc.client.Binary.encode()
        """
        import logging
        from libviri.objects import File

        logging.info('File {} saved'.format(file_name))
        return (SUCCESS, File.create(self.db,
            dict(file_name=file_name, content=file_content.data)
            )['file_id'])

    @public
    def get(self, cert, file_name_or_id):
        """Returns the content of a file"""
        import xmlrpc.client
        from libviri.objects import File

        try:
            return (SUCCESS, xmlrpc.client.Binary(
                File.get_content(self.db, file_name_or_id)))
        except File.Missing:
            return (ERROR, 'File not found')

    @public
    def ls(self, cert):
        """List files on the database"""
        from libviri.objects import File

        return (SUCCESS, File.query(self.db,
            fields=('file_name', 'file_id', 'saved'),
            order=('saved',)))

    @public
    def mv(self, cert, file_id, new_file_name):
        """Renames file with the given id"""
        import logging
        from libviri.objects import File

        if File.exists(self.db, file_id):
            logging.info('File {} renamed to {}'.format(file_id, new_file_name))
            File.update(self.db,
                {'file_name': new_file_name},
                {'file_id': file_id})
            return (SUCCESS, 'File successfully renamed')
        else:
            return (ERROR, 'File not found')

    @public
    def rm(self, cert, file_id):
        """Removes a file given its id"""
        import logging
        from libviri.objects import File

        if File.exists(self.db, file_id):
            logging.info('File {} removed'.format(file_id))
            File.delete(self.db, {'file_id': file_id})
            return (SUCCESS, 'File successfully removed')
        else:
            return (ERROR, 'File not found')

    @public
    def exists(self, cert, file_id):
        """Returns True if a file with the given id exists."""
        from libviri.objects import File

        return (SUCCESS, File.exists(self.db, file_id))

    @public
    def version(self):
        """Returns Viri version"""
        import libviri

        return (SUCCESS, libviri.__version__)

