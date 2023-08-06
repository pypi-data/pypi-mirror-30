# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Optical_Filter(Component):
    def __init__(self, parent):
        super(Optical_Filter, self).__init__(parent)
        
        self.name = 'optical filter'
        
        self.cfg_dict = {
                'OPF': 1,}
