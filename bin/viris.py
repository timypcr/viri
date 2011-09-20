# Copyright 2011, Jesús Corrius <jcorrius@gmail.com>
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

# This class implements a Microsoft Windows Service for Viri using the 
# pywin32 API in a pretty standard and uncomplicated way. To be used on 
# Windows systems instead of the demonized service used on GNU/Linux and 
# other POSIX based systems. 
#
# Useful commands (for future reference):
#
# python viris install
# python viris start
# python viris stop
# python viris remove

import os
import logging
from configparser import RawConfigParser
from libviri.rpcserver import RPCServer
from libviri.viriorm import Database
from libviri import objects

import win32service
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil

DEFAULT_CONFIG_FILE = 'virid.conf'
DEFAULTS = {
    'general': {
        'port': '6806'},
    'security': {
        'known_ca': '/etc/viri/ca.cert',
        'certKey_file': '/etc/viri/virid.pem',
        'crl_file_url': 'http://viri.atlasit.com/crl.pem'},
    'database': {
        'database_file': '/var/lib/viri/viri.db'},
    'logging': {
        'log_file': '/var/log/virid.log',
        'log_level': 'INFO',
        'log_format': '%(levelname)s::%(asctime)s::%(message)s'},
}

class ViriService(win32serviceutil.ServiceFramework):
    _svc_name_ = "Viri"
    _svc_display_name_ = "Viri Service for Windows"
    _svc_description_ = "Remote execution of Python scripts"
         
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.config_file = DEFAULT_CONFIG_FILE
        self.timeout = 3000
        self._setup()

    def SvcStop(self):
        self.rpc_server.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
         
    def SvcDoRun(self):
        import threading
        self.rpc_server = RPCServer(
            self.port,
            self.ca_file,
            self.cert_key_file,
            self.db,
            self.context)
        t = threading.Thread(target=self.rpc_server.start)
        t.daemon = True
        t.start()
        
        import servicemanager      
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        while True:
            # We loop to keep the service alive... 
            # while we regularly check for the stop signal.
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            if rc == win32event.WAIT_OBJECT_0:
                servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                      servicemanager.PYS_SERVICE_STOPPED,
                                      (self._svc_name_, ''))
                break
            
    def _setup(self):
        """Initializes all required attributes, getting the values from the
        configuration file.
        """
        
        # On Windows the current path is where PythonService.exe is located.
        # We change the current path to the location of this script.
        os.chdir(os.path.dirname(os.path.realpath( __file__ )))
        
        if not os.path.isfile(self.config_file):
            raise ValueError('Configuration file not found: {}'.format(
                self.config_file))
        
        config = RawConfigParser(DEFAULTS)
        config.read((self.config_file,))

        self.port = int(config.get('general', 'port'))
        self.ca_file = config.get('security', 'known_ca')
        self.cert_key_file = config.get('security', 'cert_key_file')
        self.crl_file_url = config.get('security', 'crl_file_url')
        self.db_file = config.get('database', 'database_file')
        self.logfile = config.get('logging', 'log_file')
        self.loglevel = config.get('logging', 'log_level')
        self.logformat = config.get('logging', 'log_format')

        if not os.path.isfile(self.ca_file):
            raise ValueError('Known CAs file not found: {}'.format(
                self.ca_file))
        if not os.path.isfile(self.cert_key_file):
            raise ValueError('Certificate and key file not found: {}'.format(
                self.cert_key_file))

        self.db = Database(self.db_file)
        if self.db.new_db:
            for obj in objects.objects:
                obj.create_table(self.db)

        conf = dict([(sc, dict(config.items(sc))) for sc in config.sections()])

        self.context = dict(conf=conf, db=self.db)
        for obj in objects.objects:
            self.context[obj.__name__] = obj

        logging.basicConfig(
            filename=self.logfile,
            format=self.logformat,
            level=getattr(logging, self.loglevel))


if __name__ == '__main__':   
    win32api.SetConsoleCtrlHandler(lambda x: True, True)
    win32serviceutil.HandleCommandLine(ViriService)

