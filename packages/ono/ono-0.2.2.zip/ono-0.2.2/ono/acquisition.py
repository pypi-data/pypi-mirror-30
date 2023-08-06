# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Acquisition(Component):
    def __init__(self, parent):
        super(Acquisition, self).__init__(parent)
        
        self.name = 'acquisition'
        
        self.cfg_dict = {
                'AQM': 'DD',
                'COR': 1,
                "DEL" : 0,
                'DLY': 0,
                "GNS": -1,
                "HFW": 8000.000000,
                "LFW": 0.000000,
                "NSS": 32,
                "REP": 1,
                "RES": 4.0}
