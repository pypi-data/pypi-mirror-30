# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Flange_Board(Component):
    def __init__(self, parent):
        super(Flange_Board, self).__init__(parent)

        self.cfg_dict = {
            'ADDRESS': 'PADDR',
            'CITY': 'CITY',
            'COUNTRY': 'CNTRY',
            'DATE': 'MANU',
            'CHANGE_LEVEL': 'IECL',
            'LOCATION': 'LOCA',
            'OWNER': 'OWNR',
            'TYPE': 'ITYPE',
            'SER': 'ISER',
            'VSN': 'FVSN',
        }
        
        self.name = 'Flange Board'
