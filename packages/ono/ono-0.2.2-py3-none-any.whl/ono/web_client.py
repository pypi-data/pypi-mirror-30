# -*- coding: utf-8 -*-

### imports ###################################################################
import logging
import os
import re
import requests
import yaml

### imports from ##############################################################
from bs4 import BeautifulSoup

logging.getLogger('webclient').addHandler(logging.NullHandler())

###############################################################################
class WebClient(object):
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('webclient')
        
        # default host
        self.host, self.port = '10.10.0.1', 80
        # self.host, self.port = '127.0.0.1', 80

        self.uri = ''

        for key, value in kwargs.items():
            if key == 'config':
                filename = value
                self.readConfig(filename)
            elif key == 'host':
                self.host = value
            elif key == 'port':
                self.port = value

        self.url_root = 'http://' + self.host
        
        if self.port:
            self.url_root = 'http://' + self.host + ':' + str(self.port)
        
        self.initSession()

        os.environ['NO_PROXY'] = self.host
        # proxies = {'http': 'http://10.2.8.131:8080'}
        # self.session.proxies.update(proxies)
        
    def initSession(self):
        self.session = requests.session()

        self.session.headers['Cache-Control'] = 'no-cache'
        self.session.headers['Connection'] = 'Keep-Alive'
        self.session.headers['Host'] = self.host

        options = '; '.join([
                'compatible',
                'MSIE 7.0',
                'Windows NT 6.1',
                'WOW64',
                'Trident/7.0',
                'SLCC2',
                '.NET CLR 2.0.50727',
                '.NET CLR 3.5.30729',
                '.NET CLR 3.0.30729',
                'Media Center PC 6.0',
                '.NET4.0C',
                '.NET4.0E'])

        self.session.headers['User-Agent'] = (
                'Mozilla/4.0 ' + '(' + options + ')')

    def find_id(self, ID):
        value = self.soup.find(id=ID)
        result = ''

        if value:
            result = value.string
        else:
            self.logger.warning("Could not find %s in %s", ID, self.uri)

        return result
    
    def get_soup(self, link, **kwargs):
        r = self.submit(link, **kwargs)
        self.soup = BeautifulSoup(r.content, 'html.parser')

        return self.soup        

    def parse_ids(self, link, **kwargs):
        self.get_soup(link, **kwargs)
        elements = self.soup.find_all(id=True)
        
        id_dict = {}

        for e in elements:
            id = e.attrs['id']
            value = e.string
            id_dict[id] = value
                   
        return id_dict

    def readConfig(self, filename):
        parameterDict = {}
        
        with open(filename) as f:
            parameterDict = yaml.load(f)

        for key, value in parameterDict.items():
            if key == 'device':
                self.device = value
                
        deviceDict = parameterDict['devices'][self.device]
        
        for key, value in deviceDict.items():
            if key == 'host':
                self.host = value
            elif key == 'name':
                self.name = value
            elif key == 'port':
                self.port = value
                
    def submit(self, url='', **kwargs):
        parameter_dict = {}
        
        for key, value in kwargs.items():
            if key in ['params', 'parameter_dict']:
                parameter_dict = value
        
        if not url:
            url = self.url_root
        elif not re.match('http://', url):
            url = '/'.join([self.url_root, url])
        
        self.uri = url
        
        if parameter_dict:
            parameter_list = []
    
            for key, value in parameter_dict.items():
                parameter = key + '=' + str(value)
                parameter_list.append(parameter)
    
            parameters = '&'.join(parameter_list)
            self.uri = '?'.join([url, parameters])
        
        r = self.session.get(self.uri)

        return r
