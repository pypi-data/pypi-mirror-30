# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class EmbeddedWebServer(Component):
    def __init__(self, parent):
        super(EmbeddedWebServer, self).__init__(parent)

        self.cfg_dict = {
            'COMMUNICATION_FORMAT_CODE': 'CFC',
            'CPU': 'WCPU',
            'DIP1': 'DIP1',
            'DIP2': 'DIP2',
            'DIP3': 'DIP3',
            'ADDRESS': 'IADR',
            'GATEWAY': 'IGTW',
            'TCP_IP_SETTINGS': 'IORI',
            'SUBNET_MASK': 'IMSK',
            'MAC_ID': 'MCID',
            'SER': 'WSER',
            'VRAM': 'WVRAM',
            'VSN': 'WVSN',
            'XTRAM': 'WXTRAM',
        }
        
        self.name = 'Embedded Web Server'

