# -*- coding: utf-8 -*-

### imports ###################################################################
import os
import unittest

### imports from ##############################################################
from hexer.hexer import create_block_config, Hexer, read_block_config

###############################################################################
class TestLMD(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_filename = os.path.join('data', 'Test_50mm.lmd')
        cls.test_cfg = os.path.join('output', 'test_lmd.cfg')
        cls.lmd_cfg = os.path.join('config', 'lmd.cfg')

        header_dict = {
                'name' : 'header',
                'size': 184,
                'structure' : [
                    [40, 'dz', '<1f'],
                    [52, 'radius', '<1f'],
                    [168, 'shape', '<2H'],
                ]
        }
        
        x_block_dict = {
                'name': 'x_scale',
                'dtype': 'f',
                'length': 'self.header.shape[0]',
        }
        
        y_block_dict = {
                'name': 'y_scale',
                'dtype': 'f',
                'length': 'self.header.shape[1]',
        }
        
        z_block_dict = {
                'name': 'Z',
                'dtype': 'f',
                'length': 'self.header.shape[0] * self.header.shape[1]',
        }
        
        cls.blocks = [
            header_dict,
            x_block_dict,
            y_block_dict,
            z_block_dict,
        ]

        create_block_config(cls.blocks, filename=cls.test_cfg)
        
    def test_00_create_config(self):
        result = create_block_config(self.blocks)
        
        self.assertEqual(type(result), str)
        self.assertEqual(len(result), 299)

    def test_01_compare_config(self):
        test_cfg = read_block_config(self.test_cfg)
        lmd_cfg = read_block_config(self.lmd_cfg)

        self.assertEqual(test_cfg, lmd_cfg)

    def test_02_lmd_blocks(self):
        hexer = Hexer(self.data_filename, name='test', blocks=self.blocks)
        hexer.readBlocks()
        self.assertEqual(self.blocks, hexer.blocks)

        Nx, Ny = hexer.header.shape
        self.assertEqual(Nx, 246)
        self.assertEqual(Ny, 246)
        
        N = len(hexer.Z.values)
        
        self.assertEqual(N, 246**2)
        
        if N:
            I_min = min(hexer.Z.values)
            I_max = max(hexer.Z.values)
            
            self.assertAlmostEqual(I_min, 0.0)
            self.assertAlmostEqual(I_max, 4.5581827)

    def test_03_lmd_config(self):
        hexer = Hexer(
                self.data_filename, name='test', config_file=self.lmd_cfg)
        
        hexer.readBlocks()

        self.assertEqual(self.blocks, hexer.blocks)
        
        self.assertEqual(self.blocks, hexer.blocks)

        Nx, Ny = hexer.header.shape
        self.assertEqual(Nx, 246)
        self.assertEqual(Ny, 246)
        
        N = len(hexer.Z.values)
        
        self.assertEqual(N, 246**2)
        
        if N:
            I_min = min(hexer.Z.values)
            I_max = max(hexer.Z.values)
            
            self.assertAlmostEqual(I_min, 0.0)
            self.assertAlmostEqual(I_max, 4.5581827)
