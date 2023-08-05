# -*- coding: utf-8 -*-

###############################################################################
import os
import unittest
from hexer.hexer import Block, Hexer

###############################################################################
class TestLMD(unittest.TestCase):
    def test_00_lmd(self):
        filename = os.path.join('data', 'Test_50mm.lmd')

        header_dict = {
                'name' : 'header',
                'size': 184,
                'structure' : (
                    (40, 'dz', '<1f'),
                    (52, 'radius', '<1f'),
                    (168, 'shape', '<2H'),
                )
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
        
        blocks = [
            header_dict,
            x_block_dict,
            y_block_dict,
            z_block_dict,
        ]

        hexer = Hexer(filename, name='test', blocks=blocks)
        hexer.readBlocks()

        self.assertEqual(hexer.header.shape[0], 246)
        self.assertEqual(hexer.header.shape[1], 246)
        
        N = len(hexer.Z.values)
        
        self.assertEqual(N, 246**2)
        
        if N:
            I_min = min(hexer.Z.values)
            I_max = max(hexer.Z.values)
            
            self.assertAlmostEqual(I_min, 0.0)
            self.assertAlmostEqual(I_max, 4.5581827)
