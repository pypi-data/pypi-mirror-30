# -*- coding: utf-8 -*-

### imports from ##############################################################
from .bruker_opus_filereader import OpusReader

###############################################################################
class Spectrum:
    def __init__(self, filename):
        self.sample = OpusReader(filename)
        self.sample.readDataBlocks()

        # spectra
        self.ab = self.sample['AB']
        self.scrf = self.sample['ScRf']
        self.scsm = self.sample['ScSm']

        # wavenumbers
        self.wavenumbers = self.sample['WN']
        self.fxv = self.sample['AB Data Parameter']['FXV']
        self.lxv = self.sample['AB Data Parameter']['LXV']
