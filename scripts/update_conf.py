""" Updates configuration file from the old version to the new one"""
import sys, os
from configparser import RawConfigParser

DEFAULT_CONF_FILE="/etc/viri/virid.conf"

class ViriScript:
    def run(self):
        try:
            config_file = DEFAULT_CONF_FILE
            if not os.path.isfile(config_file):
                raise ValueError('Configuration file not found: {0}'.format(config_file))
        
            config = RawConfigParser()
            config.read(config_file)

            if 'security' in config.sections():
                return 'The configuration file is already migrated to the new version'

            config.add_section('security')
            config.add_section('database')

            for item in config.items('paths'):
                if item[0] == 'database_file':
                    config.set('database', item[0], item[1])
                else:
                    config.set('security', item[0], item[1])
            
            config.remove_section('paths')

            config.set('security', 'crl_file_url', 'None')            
            config.set('logging', 'log_level', 'INFO')
        
            with open(config_file, 'w') as file:
                config.write(file)

        except Exception as exc:
            return exc

        return 'Configuration file migrated'
        
