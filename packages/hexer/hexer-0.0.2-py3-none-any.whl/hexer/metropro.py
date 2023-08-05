# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import os

### imports from ##############################################################
from .hexer import Hexer

###############################################################################
class MetroPro(Hexer):
    def __init__(self, filename):
        self.invalid = 2147483640
        
        filepath = os.path.realpath(__file__)
        config_path = os.path.join(os.path.dirname(filepath), 'config')
        self.metropro_cfg = os.path.join(config_path, 'metropro.cfg')
        
        self.filename = filename
        
        super(MetroPro, self).__init__(
            filename=self.filename,
            config_file=self.metropro_cfg)

    def readBlocks(self):
        super(MetroPro, self).readBlocks()

        S = self.header.inf_scale_factor
        O = self.header.obliquity_factor
        wavelength = self.header.wavelength_in

        # R = 32768 # high PhaseRes
        R = 4096 # lowPhaseRes

        self.shape = self.header.ac_height, self.header.ac_width
        self.intensity = np.array(self.intensity.values).reshape(self.shape)
        
        self.phase = np.array(self.phase.values).reshape(self.shape)
        
        self.phase_masked = np.ma.masked_where(
                self.phase >= self.invalid,
                self.phase)
        
        self.height_masked = 1E+6 * self.phase_masked * S * O * wavelength / R
