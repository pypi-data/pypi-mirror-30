# -*- coding: utf-8 -*-

### imports ###################################################################
import logging
import time

### imports from ##############################################################
from threading import Lock, Thread

### logging ###################################################################
logging.getLogger('ono').addHandler(logging.NullHandler())

### threading #################################################################
thread_lock = Lock()

###############################################################################
class VertexStatus:
    status = '---'

###############################################################################
class WaitForIdle(Thread):
    def __init__(self):
        super(WaitForIdle, self).__init__()
        
        self.logger = logging.getLogger('ono')

    def run(self):
        with thread_lock:
            VertexStatus.status = '---'

        while True:
            time.sleep(1)
            
            with thread_lock:
                status = VertexStatus.status
                
                if status == 'IDL':
                    break
                elif status == 'ERR':
                    self.logger.error('Spectrometer error: %s', status)
                    break
