import sys
import os
import logging
from optparse import OptionParser
import settings
from rpcserver import RPCServer

LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

class ViriDaemon:
    def __init__(self, port, cafile, logfile, loglevel, logformat):
        self.port = port or settings.PORT
        self.cafile = cafile or settings.CERTIFICATE_AUTHORITIES_FILENAME
        if not os.path.isfile(self.cafile):
            sys.stderr.write('Certificate file %s does not exist\n' % self.cafile)
            sys.exit(1)
        self.logfile = logfile or settings.LOG_FILENAME
        self.loglevel = loglevel or settings.LOG_LEVEL
        self.logformat = logformat or settings.LOG_FORMAT
        logging.basicConfig(
            filename=self.logfile,
            format=self.logformat,
            level=getattr(logging, self.loglevel))

    def start(self):
        logging.info('Started %s daemon on port %s' % (
            settings.APP_NAME,
            self.port)
        )
        self.server = RPCServer(
            self.port,
            self.cafile,
            settings.TASK_DIR,
            settings.DATA_DIR,
            settings.LOG_REQUESTS)
        self.server.start()

    def stop(self):
        logging.info('Stopped %s daemon' % settings.APP_NAME)


if __name__ == '__main__':
    parser = OptionParser(
        description=settings.APP_DESC,
        version=settings.APP_VERSION)
    parser.add_option('-p', '--port', dest='port',
        help='port to listen on')
    parser.add_option('-c', '--cafile', dest='cafile',
        help='authorized CA certificates')
    parser.add_option('--logfile', dest='logfile',
        help='file name where the log will be saved')
    parser.add_option('--loglevel', dest='loglevel',
        help='minimum logging level (%s)' % ', '.join(LOG_LEVELS))
    parser.add_option('--logformat', dest='logformat',
        help='logging format')
    (options, args) = parser.parse_args()

    virid = ViriDaemon(**vars(options))
    try:
        virid.start()
    except KeyboardInterrupt:
        virid.stop()

