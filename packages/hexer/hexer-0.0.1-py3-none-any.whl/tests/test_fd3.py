# -*- coding: utf-8 -*-

### imports ###################################################################
import os
import unittest

### imports from ##############################################################
from hexer.hexer import create_block_config, Hexer, read_block_config

###############################################################################
class TestFD3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_filename = os.path.join('data', 'wafer.fd3')
        cls.test_cfg = os.path.join('output', 'test_fd3.cfg')
        cls.fd3_cfg = os.path.join('config', 'fd3.cfg')

        header_dict = {
                'name' : 'header',
                'size': 224,
                'structure' : [
                    [112, 'Nx', '<1h'],
                    [116, 'Ny', '<1h'],
                    [136, 'dx', '<1d'],
                    [168, 'dy', '<1d'],
                    [200, 'dz', '<1d'],
                ]
        }
        
        
        z_block_dict = {
                'name': 'Z',
                'dtype': 'h',
                'length': 'self.header.Nx * self.header.Ny',
        }
        
        cls.blocks = [
            header_dict,
            z_block_dict,
        ]

        create_block_config(cls.blocks, filename=cls.test_cfg)

    def test_00_create_config(self):
        result = create_block_config(self.blocks)
        
        self.assertEqual(type(result), str)
        self.assertEqual(len(result), 198)

    def test_01_compare_config(self):
        test_cfg = read_block_config(self.test_cfg)
        fd3_cfg = read_block_config(self.fd3_cfg)

        self.assertEqual(test_cfg, fd3_cfg)
        
    def test_02_fd3_blocks(self):
        hexer = Hexer(self.data_filename, name='test', blocks=self.blocks)
        hexer.readBlocks()
        self.assertEqual(self.blocks, hexer.blocks)
        
        Nx, Ny = hexer.header.Nx, hexer.header.Ny
        self.assertEqual(Nx, 1624)
        self.assertEqual(Ny, 1236)
        
        N = len(hexer.Z.values)
        
        self.assertEqual(N, 1624*1236)
        
        if N:
            I_min = min(hexer.Z.values)
            I_max = max(hexer.Z.values)
            
            self.assertEqual(I_min, -10010)
            self.assertEqual(I_max, 9999)

    def test_03_fd3_config(self):
        hexer = Hexer(
                self.data_filename, name='test', config_file=self.fd3_cfg)
        
        hexer.readBlocks()

        self.assertEqual(self.blocks, hexer.blocks)
        
        Nx, Ny = hexer.header.Nx, hexer.header.Ny
        self.assertEqual(Nx, 1624)
        self.assertEqual(Ny, 1236)
        
        N = len(hexer.Z.values)
        
        self.assertEqual(N, Nx*Ny)
        
        if N:
            I_min = min(hexer.Z.values)
            I_max = max(hexer.Z.values)
            
            self.assertEqual(I_min, -10010)
            self.assertEqual(I_max, 9999)
