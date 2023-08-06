# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Fourier_Transform(Component):
    def __init__(self, parent):
        super(Fourier_Transform, self).__init__(parent)

        self.cfg_dict = {
                'PHR': 32.0,}
        
        self.name = 'Fourier Transform'
