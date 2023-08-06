# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Sample_Changer(Component):
    def __init__(self, parent):
        super(Sample_Changer, self).__init__(parent)
        
        self.name = 'sample changer'
        self._pos = 0
        self.url_diag = self.url_root + '/config/diag_autom.htm'

    def extract_status(self):
        rows = self.diag_soup.findAll('tr')

        self.connected = False
        self.initialised = False
        self._pos = 0
        
        
        for row in rows:
            td_list = row.find_all('td')

            if td_list:            
                if td_list[0].string == '14':
                    self.status = td_list[6].string
                    
                    if td_list[9].string == 'X':
                        self.initialised = True
                        
                    if td_list[10].string == 'X':
                        self.connected = True

                    if self.connected and self.initialised:    
                        self._pos = int(td_list[4].string)
                    
                    break

        self.logger.debug(
                "%s: %s status: %s", self.parent_name, self.name, self.status)

        self.logger.debug(
                "%s: %s connected: %s",
                self.parent_name, self.name, self.connected)

        self.logger.debug(
                "%s: %s initialised: %s",
                self.parent_name, self.name, self.initialised)
        
        self.logger.debug(
                "%s: %s current position: %s",
                self.parent_name, self.name, self._pos)

    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()
        self.extract_status()
        
        return self.diag_soup

    @property
    def pos(self):
        self.diagnostics()
        return self._pos

    @pos.setter
    def pos(self, snr):
        cmd = 'SNR%3D' + str(snr)
        cmd_dict = {'WRK': 8, 'UNI': cmd}

        self.parent.command(cmd_dict)
        self._pos = snr        
