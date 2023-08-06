# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .component import Component

###############################################################################
class IR_Source(Component):
    def __init__(self, parent):
        super(IR_Source, self).__init__(parent)

        self.cfg_dict = {
                'SRC': 0,}
        
        self.name = 'IR source'

        self.id_dict = {
                'date': 'HTG1SRCSDATE',
                'type': 'HTG1_SRCNAME',
                'status': 'HTG1_SRC_CURSTATE',
                'total run time': 'HTG1_SRCR',
        }

        self._src = ''

        self.url_diag = self.url_root + '/diag_SRC.htm'

    def diagnostics(self):
        self.get_diagnostics()
        self.extract_error()
        self.extract_status()
        self.extract_type()

        self.extract_total_run_time()
        self.extract_date()

        return self.diag_soup

    @property
    def src(self):
        self.diagnostics()
        return self._src

    @src.setter
    def src(self, src):
        cmd = 'SRC%3D' + str(src)
        cmd_dict = {'WRK': 8, 'UNI': cmd}

        self.parent.command(cmd_dict)
        self._src = src
