import sys
import os
import logging
import multiprocessing
from optparse import OptionParser
from configparser import RawConfigParser
from rpcserver import RPCServer
from schedserver import SchedServer

APP_NAME = 'virid'
APP_VERSION = '0.0.1'
APP_DESC = 'Accepts and executes tasks from viric instances'
LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
TASK_DIR = 'tasks'
DATA_DIR = 'data'
DEFAULT_CONFIG_FILE = '/etc/viri/virid.conf'
DEFAULTS = {
    'General': {
        'Port': '6806'},
    'Paths': {
        'PidFile': '/var/run/virid.pid',
        'KnownCAs': '/etc/viri/ca.cert',
        'WorkingDir': '/var/viri'},
    'Logging': {
        'LogFile': '/var/log/virid.log',
        'LogLevel': 'WARNING',
        'LogFormat': '%(levelname)s::%(asctime)s::%(message)s'},
}

class ViriDaemon:
    """
    """
    def __init__(self, config_file):
        self._set_config(config_file)
        self.data_dir = os.path.abspath(
            os.path.join(self.working_dir, DATA_DIR))
        self.task_dir = os.path.abspath(
            os.path.join(self.working_dir, TASK_DIR))
        self._prepare_dirs()
        logging.basicConfig(
            filename=self.logfile,
            format=self.logformat,
            level=getattr(logging, self.loglevel))

    def _set_config(self, config_file):
        config = RawConfigParser(DEFAULTS)
        config.read((config_file,))

        self.port = int(config.get('General', 'Port'))
        self.cafile = config.get('Paths', 'KnownCAs')
        self.working_dir = config.get('Paths', 'WorkingDir')
        self.logfile = config.get('Logging', 'LogFile')
        self.loglevel = config.get('Logging', 'LogLevel')
        self.logformat = config.get('Logging', 'LogFormat')

    def _prepare_dirs(self):
        """Creates the structure for the working directory, which
        contains directories for data, tasks, and a system directory
        which is used to store files like the base task or the crontab
        file. It also creates required __init__.py files.
        """
        create_dirs = (self.working_dir,
            self.data_dir,
            self.task_dir)

        for create_dir in create_dirs:
            if not os.path.isdir(create_dir):
                os.mkdir(create_dir)

        init_filename = os.path.join(self.task_dir, '__init__.py')
        if not os.path.isfile(init_filename):
            open(init_filename, 'w').close()

        if self.task_dir not in sys.path:
            sys.path.append(self.task_dir)

    def start(self):
        """Starts the ViriDaemon. It starts the SchedServer for task
        scheduling, and the RPCServer to accept connections form viric
        instances
        """
        logging.info('Started %s daemon on port %s' % (
            APP_NAME,
            self.port)
        )
        self.sched_server = SchedServer(self.data_dir)
        self.sched_server_proc = multiprocessing.Process(
            target=self.sched_server.start)
        self.sched_server_proc.start()

        self.rpc_server = RPCServer(
            self.port,
            self.cafile,
            self.data_dir,
            self.task_dir)
        self.rpc_server.start()

    def stop(self):
        self.sched_server_proc.join()
        logging.info('Stopped %s daemon' % APP_NAME)

if __name__ == '__main__':
    parser = OptionParser(
        description=APP_DESC,
        version=APP_VERSION)
    parser.add_option('-c', '--config', dest='config_file',
        help='configuration file with settings to be used by virid',
        default=DEFAULT_CONFIG_FILE)
    (options, args) = parser.parse_args()

    virid = ViriDaemon(**vars(options))

    try:
        virid.start()
    except KeyboardInterrupt:
        virid.stop()

