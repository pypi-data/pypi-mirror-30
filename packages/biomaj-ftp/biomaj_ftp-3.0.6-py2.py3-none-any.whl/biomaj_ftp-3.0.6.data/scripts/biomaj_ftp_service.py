import sys
import logging
import logging.config
import os
import yaml
import pprint

import consul
from pymongo import MongoClient
import requests
from pyftpdlib.authorizers import DummyAuthorizer, AuthenticationFailed
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from biomaj_user.user import BmajUser
from biomaj_core.utils import Utils
from biomaj_core.config import BiomajConfig


class BiomajAuthorizer(DummyAuthorizer):

    def set_config(self, cfg):
        self.cfg = cfg
        self.mongo = MongoClient(BiomajConfig.global_config.get('GENERAL', 'db.url'))
        self.db = self.mongo[BiomajConfig.global_config.get('GENERAL', 'db.name')]
        self.bank = None
        self.logger = logging

    def set_logger(self, logger):
        self.logger = logger

    def validate_authentication(self, username, apikey, handler):
        """Raises AuthenticationFailed if supplied username and
        password don't match the stored credentials, else return
        None.
        """
        # msg = "Authentication failed."
        #anonymous user : we defined the user as anonymous
        proxy = Utils.get_service_endpoint(self.cfg, 'user')
        if username == "biomaj_default":
            user = {}
            user['id'] = "BMJ_default"
        elif proxy:
            user_req = requests.get(proxy + '/api/user/info/apikey/' + apikey)
            if not user_req.status_code == 200:
                raise AuthenticationFailed('Wrong or failed authentication')
            user = user_req.json()
        else:
            user = BmajUser.get_user_by_apikey(apikey)
        if not user:
            self.logger.error('User not found: ' + username)
            raise AuthenticationFailed('User does not exists')
        
        #Determining the authorized path   
        dict_bank = {}
        for db_entry in self.db.banks.find() :
            home_dir = self.get_home_dir(username, db_entry)
            dict_bank[home_dir] = [db_entry['properties']['visibility'], db_entry['properties']['owner']]
        self.bank = dict_bank
        #Create a new user for biomaj server with specific permission
        if not self.has_user(username):
            self.add_user(username,apikey,self.get_home_dir(username))    
        for directory in dict_bank :
             if dict_bank[directory][0] == "public" :
                 perm = "elr"
                 self.override_perm(username, directory, perm, recursive=True)
             elif dict_bank[directory][1] == username and dict_bank[directory][0] != "public" :
                 perm = "elr"
                 self.override_perm(username, directory, perm, recursive=True)
             elif username == "biomaj_default" or dict_bank[directory][0] != "public" :#biomaj_default user and private bank
                 perm = ""
                 self.override_perm(username, directory, perm, recursive=True)
        return 
    def get_home_dir(self, username, bank = None):
        """Return the user's home directory.
        Since this is called during authentication (PASS),
        AuthenticationFailed can be freely raised by subclasses in case
        the provided username no longer exists.
        """
        if not bank :
            bank = self.bank
        if 'production' not in bank :
            list_home_dir = []           
            for key in bank :
                list_home_dir.append(key)
            home_dir = os.path.commonprefix(list_home_dir)
            return home_dir
        last = bank['production'][0]
        if bank['current']:
            for prod in bank['production']:
                if prod['session'] == bank['current']:
                    last = prod
                    break
        home_dir = os.path.join(last['data_dir'], last['dir_version'])
        if sys.version_info.major == 2:
            home_dir = home_dir.encode('utf-8')
        return home_dir

    def get_msg_login(self, username):
        """Return the user's login message."""
        return 'Welcome to BioMAJ FTP'

    def get_msg_quit(self, username):
        """Return the user's quitting message."""
        return 'Bye'


class BiomajFTP(object):

    def __init__(self):
        config_file = 'config.yml'
        if 'BIOMAJ_CONFIG' in os.environ:
            config_file = os.environ['BIOMAJ_CONFIG']
        self.cfg = None
        with open(config_file, 'r') as ymlfile:
            self.cfg = yaml.load(ymlfile)
            Utils.service_config_override(self.cfg)

        # There is an issue with tcp checks, see https://github.com/cablehead/python-consul/issues/136
        if self.cfg['consul']['host']:
            consul_agent = consul.Consul(host=self.cfg['consul']['host'])
            consul_agent.agent.service.register('biomaj-ftp',
                service_id=self.cfg['consul']['id'],
                address=self.cfg['consul']['id'],
                port=self.cfg['ftp']['port'],
                tags=['biomaj'])
            check = consul.Check.tcp(host= self.cfg['consul']['id'],
                port=self.cfg['ftp']['port'],
                interval=20)
            consul_agent.agent.check.register(self.cfg['consul']['id'] + '_check',
                check=check,
                service_id=self.cfg['consul']['id'])

        if self.cfg['log_config'] is not None:
            for handler in list(self.cfg['log_config']['handlers'].keys()):
                self.cfg['log_config']['handlers'][handler] = dict(self.cfg['log_config']['handlers'][handler])
            logging.config.dictConfig(self.cfg['log_config'])
        self.logger = logging.getLogger('biomaj')

        BiomajConfig.load_config(self.cfg['biomaj']['config'])

        BmajUser.set_config(self.cfg)

        authorizer = BiomajAuthorizer()
        authorizer.set_config(self.cfg)
        authorizer.set_logger(self.logger)

        self.handler = FTPHandler
        self.handler.authorizer = authorizer
        if 'passive_ports_start' in self.cfg['ftp'] and 'passive_ports_end' in self.cfg['ftp'] and self.cfg['ftp']['passive_ports_start'] and self.cfg['ftp']['passive_ports_end']:
            self.handler.passive_ports = range(self.cfg['ftp']['passive_ports_start'], self.cfg['ftp']['passive_ports_end'])
            self.logger.info('Use passive ports range %d:%d' % (self.cfg['ftp']['passive_ports_start'], self.cfg['ftp']['passive_ports_end']))
        else:
            self.handler.passive_ports = range(60000, 65535)
            self.logger.info('Use passive ports range %d:%d' % (60000, 65535))
        
        masquerade_address = os.environ.get('MASQUERADE_ADDRESS', None)
        if masquerade_address:
            self.handler.masquerade_address = os.environ['MASQUERADE_ADDRESS']
        elif 'masquerade_address' in self.cfg['ftp'] and self.cfg['ftp']['masquerade_address'] is not None:
            self.handler.masquerade_address = self.cfg['ftp']['masquerade_address']

    def start(self):
        server = FTPServer((self.cfg['ftp']['listen'], self.cfg['ftp']['port']), self.handler)
        server.serve_forever()


ftp_handler = BiomajFTP()
ftp_handler.start()
