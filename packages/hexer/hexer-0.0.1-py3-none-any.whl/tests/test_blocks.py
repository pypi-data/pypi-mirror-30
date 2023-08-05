# -*- coding: utf-8 -*-

###############################################################################
import os
import unittest
from hexer.hexer import Block, Hexer

###############################################################################
class TestBlocks(unittest.TestCase):

    def test_00_float_block(self):
        filename = os.path.join('data', 'w699.0')
        hexer = Hexer(filename)

        offset, size = 144, 303320 # 75830 x float32
        offset_1 = offset + size
    
        buffer = hexer.data[offset:offset_1]
        block = Block(buffer, fmt='<75800f')
        block.readBuffer()
        
        N = len(block.values)
        self.assertEqual(N, 75800)

        if N:
            I_min = min(block.values)
            I_max = max(block.values)
            
            self.assertAlmostEqual(I_min, -5.0504503)
            self.assertAlmostEqual(I_max,  5.8987002)

    def test_01_chunk_block(self):
        filename = os.path.join('data', 'w699.0')
        hexer = Hexer(filename)
        
        offset, size = 304312, 564
        offset_1 = offset + size
        
        buffer = hexer.data[offset:offset_1]

        chunk_dict = {
            'dtype_dict':
                {0: '<i', 1: '<d', 2: 'utf-8', 3: 'utf-8', 4: 'utf-8'},

            'structure': (
                ('name', 0, 3, 'utf-8'),
                ('dtype_key', 4, 2, '<H'),
                ('size', 6, 2, '<H'),
                ('value', 8, '2*self.size', 'self.dtype_dict[self.dtype_key]'),
            ),
            
            'terminator': 'END',
        }

        block = Block(buffer, chunk_dict=chunk_dict)
        values = block.readBuffer()

    def test_02_header_block(self):
        filename = os.path.join('data', 'w699.0')
        hexer = Hexer(filename)

        structure = (
            ('magic', 0, '<2H'),
            ('block_offset', 12, '<1I'),
            ('no_of_blocks', 20, '<I'),
        )
        
        buffer = hexer.data[0:144]
        header = Block(buffer, structure=structure)
        
