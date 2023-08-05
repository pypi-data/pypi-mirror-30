# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np
import os
import unittest

### imports from ##############################################################
from hexer.metropro import MetroPro

###############################################################################
class TestMetroPro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_filename = os.path.join('data', '50x_2_J0883_1.dat')

        cls.hexer = MetroPro(cls.data_filename)
        cls.hexer.readBlocks()

    def test_01_metropro_config(self):
        header = self.hexer.header
        
        self.assertEqual(header.magic_number, 2283471727)
        self.assertEqual(header.header_format, 1)
        self.assertEqual(header.header_size, 834)

        self.assertEqual(header.swinfo_version_major, 8)
        self.assertEqual(header.swinfo_version_minor, 1)
        self.assertEqual(header.swinfo_version_bug, 1)

        self.assertEqual(header.ac_width, 640)
        self.assertEqual(header.ac_height, 480)
        self.assertEqual(header.ac_n_buckets, 1)
        self.assertEqual(header.ac_range, 255)
        self.assertEqual(header.ac_n_bytes, 2*640*480)

        self.assertEqual(header.cn_width, 640)
        self.assertEqual(header.cn_height, 480)
        self.assertEqual(header.cn_n_bytes, 4*640*480)
        
        self.assertAlmostEqual(header.inf_scale_factor, 0.5)
        self.assertAlmostEqual(header.obliquity_factor, 1.0)
        self.assertAlmostEqual(header.lateral_res, 1.0981697E-7)
        self.assertAlmostEqual(header.wavelength_in, 6.480E-7)

        phase_max = np.max(self.hexer.phase)
        self.assertEqual(phase_max, 2147483640)