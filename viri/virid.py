import sys
import os
import logging
from optparse import OptionParser
from rpcserver import RPCServer

APP_NAME = 'virid'
APP_VERSION = '0.0.1'
APP_DESC = 'Accepts and executes tasks from a viric instance'

PID_FILE = '/var/run/virid.pid' # XXX Not sure if the pid shold be managed here
DEFAULT_KNOWN_CA_FILE = 'keys/ca.cert'
TASK_DIR = 'tasks' # FIXME allow to set as an argument
DATA_DIR = 'data' # FIXME allow to set as an argument

DEFAULT_PORT = 6808
DEFAULT_LOG_FILE = None
DEFAULT_LOG_LEVEL = 'DEBUG'
DEFAULT_LOG_FORMAT = '%(levelname)s::%(asctime)s::%(message)s'

LOG_REQUESTS = False
LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

class ViriDaemon:
    """
    """
    def __init__(self, port, cafile, logfile, loglevel, logformat):
        self.port = port
        self.cafile = cafile
        if not os.path.isfile(self.cafile):
            sys.stderr.write('Certificate file %s does not exist\n' % self.cafile)
            sys.exit(1)
        self.logfile = logfile
        self.loglevel = loglevel
        self.logformat = logformat
        logging.basicConfig(
            filename=self.logfile,
            format=self.logformat,
            level=getattr(logging, self.loglevel))

    def start(self):
        logging.info('Started %s daemon on port %s' % (
            APP_NAME,
            self.port)
        )
        self.server = RPCServer(
            self.port,
            self.cafile,
            TASK_DIR,
            DATA_DIR,
            LOG_REQUESTS)
        self.server.start()

    def stop(self):
        logging.info('Stopped %s daemon' % APP_NAME)


if __name__ == '__main__':
    parser = OptionParser(
        description=APP_DESC,
        version=APP_VERSION)
    parser.add_option('-p', '--port', dest='port',
        help='port to listen on', type='int', default=DEFAULT_PORT)
    parser.add_option('-c', '--cafile', dest='cafile',
        help='authorized CA certificates', default=DEFAULT_KNOWN_CA_FILE)
    parser.add_option('--logfile', dest='logfile',
        help='file name where the log will be saved', default=DEFAULT_LOG_FILE)
    parser.add_option('--loglevel', dest='loglevel',
        help='minimum logging level (%s)' % ', '.join(LOG_LEVELS),
        default=DEFAULT_LOG_LEVEL)
    parser.add_option('--logformat', dest='logformat',
        help='logging format', default=DEFAULT_LOG_FORMAT)
    (options, args) = parser.parse_args()

    if not os.path.isfile(options.cafile):
        sys.stderr.write('Certificate file %s does not exist\n' % options.cafile)
        sys.exit(1)

    virid = ViriDaemon(**vars(options))
    try:
        virid.start()
    except KeyboardInterrupt:
        virid.stop()

