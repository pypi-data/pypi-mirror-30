# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Measurement_Channel(Component):
    def __init__(self, parent):
        super(Measurement_Channel, self).__init__(parent)
        
        self.name = 'sample compartment'
        
        self.cfg_dict = {
                'CHN': 1,}
