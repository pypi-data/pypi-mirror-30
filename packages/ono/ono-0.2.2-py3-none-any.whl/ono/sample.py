# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Sample(Component):
    def __init__(self, parent):
        super(Sample, self).__init__(parent)
        
        self.name = 'sample'
        
        self.cfg_dict = {
                "CNM": "operator",
                "SFM": "sample+form",
                'SNM': 'sample',
                "SOT" : "0",}
