import logging
from optparse import OptionParser
import settings
from rpcserver import RPCServer

LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

class ViriDaemon:
    def __init__(self, port, logfile, loglevel, logformat):
        self.port = port or settings.PORT
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

