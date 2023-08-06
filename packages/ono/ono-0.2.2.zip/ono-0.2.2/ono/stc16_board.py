# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class STC16_Board(Component):
    def __init__(self, parent):
        super(STC16_Board, self).__init__(parent)

        self.cfg_dict = {
            'VSN': 'DVSN',
        }
        
        self.name = 'STC16 Board'
