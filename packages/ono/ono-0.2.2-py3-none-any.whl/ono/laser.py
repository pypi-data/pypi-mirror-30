# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Laser(Component):
    def __init__(self, parent):
        super(Laser, self).__init__(parent)
        
        self.name = 'laser'
       
        self.id_dict['status'] = 'IFLSRCURSTATE'
        self.id_dict['total run time'] = 'IFLSRR'
        self.id_dict['date'] = 'IFLSRSDATE'
        self.url_diag = self.url_root + '/config/diag_laser.htm'

    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()
        self.extract_status()
        
        self.extract_total_run_time()
        self.extract_date()
        
        return self.diag_soup

