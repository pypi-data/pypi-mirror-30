# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Apertur(Component):
    def __init__(self, parent):
        super(Apertur, self).__init__(parent)
        
        self.name = 'apertur wheel'
        
        self.cfg_dict = {
                'APT': 250,}
