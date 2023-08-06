# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class BMS(Component):
    def __init__(self, parent):
        super(BMS, self).__init__(parent)
        
        self.name = 'beam splitter'

        self.cfg_dict = {
                'BMS': 1,}
        
        self.id_dict['auto_recognition_id'] = 'AAR_BMS'
        self.id_dict['device_id'] = 'BMS1_BMSID'
        self.id_dict['status'] = 'BMS1_SELECT'
        self.id_dict['type'] = 'BMS1_TYPE'
        
        self.url_diag = self.url_root + '/config/diag_BMS.htm'

    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()

        # Error in diag_bms.htm: <TD> </TD> missing
        # self.extract_status()
        self.extract_device_id()
        self.extract_type()

        return self.diag_soup

    def recognize(self):
        aar_id = self.id_dict['auto_recognition_id']
        aar_str = self.parent.web_cfg_dict.pop(aar_id)

        param_list = aar_str[2:-1].split('@*!')
        
        for p in param_list:
            key, value = p.split('=')
            setattr(self, key, value)
