# -*- coding: utf-8 -*-

### imports ###################################################################
import os
import unittest

### imports from ##############################################################
from hexer.hexer import create_config, Hexer, read_block_config

###############################################################################
class TestBrukerOpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_filename = os.path.join('data', 'w699.0')
        cls.test_cfg = os.path.join('output', 'test_bruker_opus.cfg')

        cls.bruker_opus_cfg = os.path.join(
                'hexer', 'config', 'bruker_opus.cfg')

        block_desc = {
            'name': 'block_desc',
            'loop': 7,
            'size': 12,
            'structure': [
                [0, 'block_type', '<1I'],
                [4, 'block_size', '<1I'],
                [8, 'offset', '<1I'],
            ]
        }

        header_dict = {
                'name' : 'header',
                'size': 144,
                'structure' : [
                    [0, 'magic_numbers', '<2H'],
                    [12, 'block_offset', '<1I'],
                    [20, 'no_of_blocks', '<1I'],
                    [24, 'block_desc', 'chunk']
                ]
        }
        
        z_block_dict = {
                'name': 'spectrum',
                'dtype': '<f',
                'length': 75830,
        }

        
        cls.blocks = [
            header_dict,
            z_block_dict,
        ]

        chunks = {'block_desc': block_desc}

        cls.config = {'chunks': chunks, 'blocks': cls.blocks}
        create_config(cls.config, filename=cls.test_cfg)
        
    def test_00_create_config(self):
        result = create_config(self.config)
        
        self.assertEqual(type(result), str)
        self.assertEqual(len(result), 365)

    def test_01_compare_config(self):
        test_cfg = read_block_config(self.test_cfg)
        bruker_opus_cfg = read_block_config(self.bruker_opus_cfg)

        self.assertEqual(test_cfg, bruker_opus_cfg)

    def test_02_bruker_opus_blocks(self):
        hexer = Hexer(self.data_filename, name='test', blocks=self.blocks)
        hexer.readBlocks()
        self.assertEqual(self.blocks, hexer.blocks)

        N = len(hexer.spectrum.values)
        
        self.assertEqual(N, 75830)
        
        if N:
            I_min = min(hexer.spectrum.values)
            I_max = max(hexer.spectrum.values)
            
            self.assertAlmostEqual(I_min, -5.0504503)
            self.assertAlmostEqual(I_max,  5.8987002)

    def test_03_bruker_opus_config(self):
        hexer = Hexer(
                self.data_filename, name='test',
                config_file=self.bruker_opus_cfg)
        
        hexer.readBlocks()

        print('blocks')
        print(self.blocks)
        print('hexer.blocks')
        print(hexer.blocks)

        self.assertEqual(self.blocks, hexer.blocks)

        
        N = len(hexer.spectrum.values)
        
        self.assertEqual(N, 75830)
        
        if N:
            I_min = min(hexer.spectrum.values)
            I_max = max(hexer.spectrum.values)
            
            self.assertAlmostEqual(I_min, -5.0504503)
            self.assertAlmostEqual(I_max, 5.8987002)
