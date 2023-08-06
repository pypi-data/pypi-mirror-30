# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class Detector(Component):
    def __init__(self, parent, pos=1):
        super(Detector, self).__init__(parent)
        
        self.auto_recognition_id = 'AAR_DTC'

        self.cfg_dict = {
                "CFE": 0,
                "DTC" : 16416,
                "HPF": 0,
                "LPF": 10000,
                "PGN": 0}

        self.id_dict['status'] = 'HTG' + str(pos) + '_DTC_SEL'

        self.name = 'detector ' + str(pos)
        self.pos = pos
        self.url_diag = self.url_root + '/diag_DTC.htm'


    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()
        self.extract_status()
        
        return self.diag_soup

    def recognize(self):
        aar_str = self.parent.web_cfg_dict[self.auto_recognition_id]

        param_list = aar_str[2:-1].split('@*!')
        
        self.idc_list = []
        
        for row, p in enumerate(param_list):
            key, value = p.split('=')
            
            if key == 'IDC':
                self.idc_list.append(row)

        i0 = self.idc_list[self.pos - 1]
        N = len(self.idc_list)
        
        if self.pos < N:
            i1 = self.idc_list[self.pos]
        else:
            i1 = len(param_list)

        for p in param_list[i0:i1]:
            key, value = p.split('=')
            setattr(self, key, value)

