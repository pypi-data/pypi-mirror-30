# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Scanner(Component):
    def __init__(self, parent):
        super(Scanner, self).__init__(parent)

        self.cfg_dict = {
                'VEL': 5000,}
        
        self.id_dict['status'] = 'DSPSTA'
        self.name = 'scanner'
        self.url_diag = self.url_root + '/config/diag_scan.htm'

    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()
        self.extract_status()
        self.extract_config()

        return self.diag_soup
        
    def extract_config(self):
        rows = self.diag_soup.findAll('tr')

        for row in rows:
            td_list = row.find_all('td')

            for i, td in enumerate(td_list):
                if td.string == 'Position [fringes]':
                    self.peak_forward = int(float(td_list[i+2].string))
                    self.peak_backward = int(float(td_list[i+4].string))
                elif td.string == 'Main control 2':                    
                    self.cfg_dict['VEL'] = int(row.contents[3].string)

        self.logger.debug(
                "%s: %s forward peak: %i",
                self.parent_name, self.name, self.peak_forward)

        self.logger.debug(
                "%s: %s backward peak: %i",
                self.parent_name, self.name, self.peak_backward)
