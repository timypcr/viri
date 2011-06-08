#!/usr/bin/env python3
import sys
import os
import logging
import multiprocessing
from optparse import OptionParser
from configparser import RawConfigParser
from viri.scriptmanager import ScriptManager
from viri.rpcserver import RPCServer
from viri.schedserver import SchedServer

APP_NAME = 'virid'
APP_VERSION = '0.0.1'
APP_DESC = 'Receives and executes scripts from viric instances'
LOG_LEVELS = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
SCRIPT_DIR = 'script'
INFO_DIR = 'info'
DATA_DIR = 'data'
DEFAULT_CONFIG_FILE = '/etc/viri/virid.conf'
DEFAULTS = {
    'General': {
        'Port': '6806'},
    'Paths': {
        'KnownCAs': '/etc/viri/ca.cert',
        'CertKeyFile': '/etc/viri/virid.pem',
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
        config = RawConfigParser(DEFAULTS)
        config.read((config_file,))

        self.port = int(config.get('General', 'Port'))
        self.ca_file = config.get('Paths', 'KnownCAs')
        self.cert_key_file = config.get('Paths', 'CertKeyFile')
        self.working_dir = config.get('Paths', 'WorkingDir')
        self.logfile = config.get('Logging', 'LogFile')
        self.loglevel = config.get('Logging', 'LogLevel')
        self.logformat = config.get('Logging', 'LogFormat')

        conf = None
        if config.has_section('Custom'):
            Conf = type('Conf', tuple(), {})
            conf = Conf()
            for key, val in dict(config.items('Custom')).items():
                if key not in DEFAULTS.keys():
                    setattr(conf, key, val)

        self.script_dir = os.path.abspath(
            os.path.join(self.working_dir, SCRIPT_DIR))
        self.info_dir = os.path.abspath(
            os.path.join(self.working_dir, INFO_DIR))
        self.data_dir = os.path.abspath(
            os.path.join(self.working_dir, DATA_DIR))

        self.context = {}
        self.context['conf'] = conf
        self.context['data_dir'] = self.data_dir

        self.script_manager = ScriptManager(
            self.script_dir, self.info_dir, self.context)

        self._prepare_dirs()

        logging.basicConfig(
            filename=self.logfile,
            format=self.logformat,
            level=getattr(logging, self.loglevel))

    def _prepare_dirs(self):
        """Creates the structure for the working directory, which
        contains directories for data, tasks, and a system directory
        which is used to store files like the base task or the crontab
        file. It also creates required __init__.py files.
        """
        create_dirs = (self.working_dir,
            self.script_dir,
            self.info_dir,
            self.data_dir)

        for create_dir in create_dirs:
            if not os.path.isdir(create_dir):
                os.mkdir(create_dir)

        init_filename = os.path.join(self.script_dir, '__init__.py')
        if not os.path.isfile(init_filename):
            open(init_filename, 'w').close()

        if self.script_dir not in sys.path:
            sys.path.append(self.script_dir)

    def start(self):
        """Starts the ViriDaemon. It starts the SchedServer for task
        scheduling, and the RPCServer to accept connections form viric
        instances
        """
        logging.info('Started %s daemon on port %s' % (
            APP_NAME,
            self.port)
        )
        self.sched_server = SchedServer(
            self.data_dir, self.context)
        self.sched_server_proc = multiprocessing.Process(
            target=self.sched_server.start)
        self.sched_server_proc.start()

        self.rpc_server = RPCServer(
            self.port,
            self.ca_file,
            self.cert_key_file,
            self.script_dir,
            self.data_dir,
            self.script_manager)
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

