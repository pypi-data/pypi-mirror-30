# -*- coding: utf-8 -*-

### imports ###################################################################
import datetime
import logging
import requests
import shutil
import time
import yaml

### relative imports from #####################################################
from .acquisition import Acquisition
from .apertur import Apertur
from .beam_splitter import BMS
from .detector import Detector
from .embedded_webserver import EmbeddedWebServer
from .flange_board import Flange_Board
from .fourier_transform import Fourier_Transform
from .ir_source import IR_Source
from .laser import Laser
from .measurement_channel import Measurement_Channel
from .optical_filter import Optical_Filter
from .sample import Sample
from .sample_changer import Sample_Changer
from .scanner import Scanner
from .stc16_board import STC16_Board
from .web_client import WebClient

###############################################################################
class Spectrometer(WebClient):
    def __init__(self, **kwargs):
        super(Spectrometer, self).__init__(**kwargs)
        
        self.logger = logging.getLogger('bruker')

        # default values
        self._filename = ''
        self.links_path_dict = {}
        self.name = ''
        self.paths = {}
        self._rest_scans = 0
        self._rest_time = 0.0
        self._status = 'IDL'
        
        self.url_brow_stat = ''
        self.url_cmd = ''
        self.url_msg = ''
        self.url_opuslinks = ''
        self.url_stat = ''
        
        self._web_cfg_dict = {}

        if 'config' in kwargs.keys():
            filename = kwargs['config']
            self.readConfig(filename)

        self.initUrls()
        self.initSession()
        self.initComponents()
        self.initConfig()
        
        self.measurement_background = {
                "WRK" : 1,
                "AMD" : 7,
                "UWN" : 1,
                "ITC" : 1,
                "SFM" : "background",
                "DEL" : 0,
                "LPF" : 10.0,
                "VEL" : 5.00,
                "SON" : 0,
                "CMA" : 4,
                "LCL" : 0,
                "LCH" : 32768,
                "RDX" : 0,
                "TSR" : 256,
                "REP" : 1,
                "DDM" : 0,
                "DLR" : 0}

        self.cfg_optics = {"MDS": 0, "SON": 0}

        self.measurement_browser = {   
                 "DIS" : "-10",
                 "WRK" : "Start+Measurement"}

        self.measurement_browser.update(self.ir_source.cfg_dict)
        self.measurement_browser.update(self.apertur.cfg_dict)
        self.measurement_browser.update(self.beam_splitter.cfg_dict)
        self.measurement_browser.update(self.scanner.cfg_dict)
        self.measurement_browser.update(self.sample_compartment.cfg_dict)
        self.measurement_browser.update(self.first_detector.cfg_dict)
        self.measurement_browser.update(self.cfg_optics)
        self.measurement_browser.update(self.sample.cfg_dict)
        self.measurement_browser.update(self.acquisition.cfg_dict)

    def initConfig(self):
        self.ctrler_cfg_dict = self.parse_ids(self.url_cfg_controller)
        self.embedded_webserver.get_ctrler_config()

    def initComponents(self):
        # Spectrometer components
        self.acquisition = Acquisition(self)
        self.apertur = Apertur(self)
        self.beam_splitter = BMS(self)
        self.first_detector = Detector(self)
        self.second_detector = Detector(self, 2)
        self.embedded_webserver = EmbeddedWebServer(self)
        self.flange_board = Flange_Board(self)
        self.fourier_transform = Fourier_Transform(self)
        self.ir_source = IR_Source(self)
        self.laser = Laser(self)
        self.optical_filter = Optical_Filter(self)
        self.sample = Sample(self)
        self.sample_changer = Sample_Changer(self)    
        self.sample_compartment = Measurement_Channel(self)
        self.scanner = Scanner(self)
        self.stc16_board = STC16_Board(self)

    def initUrls(self):
        self.setUrls(self.paths)
        self.getOpusLinks()

        opus_paths = {}

        for path_id, path in self.opus_links.items():
            key = self.links_path_dict[path_id]
            opus_paths[key] = path

        self.setUrls(opus_paths)
        self.paths.update(opus_paths)
    
    def beep(self):
        r = self.submit(self.url_beep)
        self.logger.debug("%s: BEEP! BEEP! BEEP!", self.name)
        return r

    def browser_abort(self):
        return self.submit(self.url_brow_stat, params={'sub': 'Abort'})
    
    def browser_measure(self):
        return self.submit(self.url_brow_cmd, params=self.measurement_browser)

    def browser_stop(self):
        return self.submit(self.url_brow_stat, params={'sub': 'Stop'})

    def connect(self):
        # connect
        now = datetime.datetime.utcnow()
        utc = int((now - datetime.datetime(1970, 1, 1)).total_seconds())

        parameter_dict = {
                'UTC': utc, 'TIZ': 3600, 'DAL': 3600, 'IAM': 'RM402%2dANLAGE'}

        self.setConfig(parameter_dict)
        
        self.submit(self.url_stat)
        self.submit(self.url_msg)
        self.submit(self.url_opt_comp)
        self.submit(self.url_diag)
        self.submit(self.url_stat)
        self.submit(self.url_msg)
        self.submit(self.url_stat)
        
        parameter_dict = {'WRK': 8, 'UNI': 'ITC%3d1'}
        
        self.submit(self.url_cmd, params=parameter_dict)
        
        self.submit(self.url_stat)
        r = self.submit(self.url_msg)

        return r
    
    def command(self, parameter_dict):
        r = self.submit(self.url_cmd, params=parameter_dict)

        return r

    def getCommandList(self):
        soup = self.get_soup(self.url_cfg_cmdlist)
        # self.cmd_ids = self.parse_ids(self.url_cfg_cmdlist).keys()
        self._apt = int(soup.find(id='APT').parent.find_all('td')[3].string)
        self._flp = int(soup.find(id='FLP').parent.find_all('td')[3].string)
        self._lsr = int(soup.find(id='LSR').parent.find_all('td')[3].string)
        self._opf = int(soup.find(id='OPF').parent.find_all('td')[3].string)

    def getConfig(self):
        self.web_cfg_dict = self.parse_ids(self.url_cfg)
        return self.web_cfg_dict

    def getLastMessage(self, as_string=False):
        self.lastMessage = self.parse_ids(self.url_msg)

        sender = 'Vertex 70'
        message = 'all ok'
    
        for key, value in self.lastMessage.items():
            if key == 'EMSG':
                message = value
            elif key == 'ESEN':
                sender = value
    
        full_message = ': '.join([sender, message])
        
        return full_message

    def getOpusLinks(self):
        # get opus links
        self.opus_links = self.parse_ids(self.url_opuslinks)

    def getStatus(self):
        self._scans = 0
        
        self.get_soup(self.url_stat)

        self.stat_ids = self.parse_ids(self.url_stat)
        
        for key, value in self.stat_ids.items():
            if key == 'DAFI':
                self._filename = value
            elif key == 'MSTCO':
                self._status = value
            elif key == 'NCFG':
                self._ncfg = int(value)
            elif key == 'NERR':
                self._nerr = int(value)
            elif key == 'SCAN':
                self._scans = int(value)
            elif key == 'SRSC':
                self._rest_scans = int(value)
            elif key == 'SRTI':
                self._rest_time = float(value)
                
        # self._rest_scans = int(self.find_id('SRSC'))
        # self._rest_time = float(self.find_id('SRTI'))

        return self.soup
    
    def measure(self, exp_name = 'alignment'):
        experiment = self.measurements[exp_name]
        
        self.submit(self.url_cmd, params=experiment)
       
    def downloadFile(self, destiny='../output/test.0'):
        filename = self._filename
        self.url_spectrum = self.url_root + '/' + filename
        
        r = requests.get(self.url_spectrum, stream=True)

        if r.status_code == 200:
            with open(destiny, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
                
        return r

    def readConfig(self, filename):
        parameterDict = {}
        
        with open(filename) as f:
            parameterDict = yaml.load(f)

        for key, value in parameterDict.items():
            if key == 'device':
                self.device = value
            elif key == 'links_path_dict':
                self.links_path_dict = value
            elif key == 'measurements':
                self.measurements = value
            elif key == 'paths':
                self.paths = value

        deviceDict = parameterDict['devices'][self.device]
        
        for key, value in deviceDict.items():
            if key == 'host':
                self.host = value
            elif key == 'name':
                self.name = value
            elif key == 'port':
                self.port = value

    def setConfig(self, parameter_dict):
        self.web_cfg_dict = self.parse_ids(self.url_cfg, params=parameter_dict)
        return self.web_cfg_dict

    def setUrls(self, paths):
        for key, path in paths.items():
            name = '_'.join(('url', key))
            url = '/'.join((self.url_root, path))
            setattr(self, name, url)

    ### properties ############################################################
    @property
    def APT(self):
        time.sleep(0.1)
        self.getCommandList()
        return self._apt

    @APT.setter
    def APT(self, value):
        UNI = 'APT=' + str(value)
        
        params = {
            'submit': 'Send+command+line',
            'UNI': UNI,
        }        

        self.submit(self.url_directcmd, params=params)

    @property
    def FLP(self):
        time.sleep(0.1)
        self.getCommandList()
        return self._flp

    @FLP.setter
    def FLP(self, value):
        UNI = 'FLP=' + str(value)
        
        params = {
            'submit': 'Send+command+line',
            'UNI': UNI,
        }        

        self.submit(self.url_directcmd, params=params)

    @property
    def LSR(self):
        time.sleep(0.1)
        self.getCommandList()
        return self._lsr

    @LSR.setter
    def LSR(self, value):
        UNI = 'LSR=' + str(value)
        
        params = {
            'submit': 'Send+command+line',
            'UNI': UNI,
        }        

        self.submit(self.url_directcmd, params=params)

    @property
    def OPF(self):
        time.sleep(0.1)
        self.getCommandList()
        return self._opf

    @OPF.setter
    def OPF(self, value):
        UNI = 'OPF=' + str(value)
        
        params = {
            'submit': 'Send+command+line',
            'UNI': UNI,
        }        

        self.submit(self.url_directcmd, params=params)
        
    @property
    def rest_scans(self):
        self.getStatus()
        return self._rest_scans
    
    @property
    def rest_time(self):
        self.getStatus()
        return self._rest_time
        
    @property
    def status(self):
        self.getStatus()
        return self._status

    @property
    def web_cfg_dict(self):
        return self._web_cfg_dict
    
    @web_cfg_dict.setter
    def web_cfg_dict(self, parameter_dict):
        self._web_cfg_dict = parameter_dict
        
        self.flange_board.get_config()
        self.stc16_board.get_config()
        
        self.beam_splitter.recognize()
        self.first_detector.recognize()
        self.second_detector.recognize()

    @property
    def ctrler_cfg_dict(self):
        return self._ctrler_cfg_dict
    
    @ctrler_cfg_dict.setter
    def ctrler_cfg_dict(self, parameter_dict):
        self._ctrler_cfg_dict = parameter_dict
