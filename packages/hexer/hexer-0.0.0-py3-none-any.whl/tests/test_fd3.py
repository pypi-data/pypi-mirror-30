# -*- coding: utf-8 -*-

###############################################################################
import os
import unittest
from hexer.hexer import Block, Hexer

###############################################################################
class TestLMD(unittest.TestCase):
    def test_00_fd3(self):
        filename = os.path.join('data', 'wafer.fd3')

        header_dict = {
                'name' : 'header',
                'size': 224,
                'structure' : (
                    (112, 'Nx', '<1h'),
                    (116, 'Ny', '<1h'),
                    (136, 'dx', '<1d'),
                    (168, 'dy', '<1d'),
                    (200, 'dz', '<1d'),
                )
        }
        
        
        z_block_dict = {
                'name': 'Z',
                'dtype': 'h',
                'length': 'self.header.Nx * self.header.Ny',
        }
        
        blocks = [
            header_dict,
            z_block_dict,
        ]

        hexer = Hexer(filename, name='test', blocks=blocks)
        hexer.readBlocks()
        
        Nx = hexer.header.Nx
        self.assertEqual(Nx, 1624)
        Ny = hexer.header.Ny
        self.assertEqual(Ny, 1236)
        
        N = len(hexer.Z.values)
        
        self.assertEqual(N, Nx*Ny)
        
        if N:
            I_min = min(hexer.Z.values)
            I_max = max(hexer.Z.values)
            
            self.assertEqual(I_min, -10010)
            self.assertEqual(I_max, 9999)
