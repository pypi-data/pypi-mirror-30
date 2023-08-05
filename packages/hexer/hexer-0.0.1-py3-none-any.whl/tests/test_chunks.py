# -*- coding: utf-8 -*-

###############################################################################
import os
import unittest
from hexer.hexer import Chunk, Hexer

###############################################################################
class TestChunks(unittest.TestCase):

    def test_chunks(self):
        filename = os.path.join('data', 'w699.0')
    
        hexer = Hexer(filename)

        # offset, size = 303664, 336 # 0x54
        # dtype, size = 3, 2 : SGN, SG2, AQM, COR, SOT 
    
        # offset, size = 304000, 220
        # dtype = 3 : VEL, PGN, HPF, LPF
        # dtype = 4 : SRC, APT, BMS, CHN, DTC, SON, CFE, CFO
        
        # offset, size = 304220, 250
        # dtype = 3 : PHZ, APF, ZFF

        offset, size = 304312, 564
        # dtype = 2 : INS, VSN, VSD, SRN

        # offset, size = 304876, 55
        # dtype = 2 : SNM, SFM, CNM
        
        offset_1 = offset + size

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

        print()
        
        while offset < offset_1:
            buffer = hexer.data[offset:offset_1]
        
            chunk = Chunk(buffer, chunk_dict=chunk_dict)
            chunk_size = chunk.readBuffer()
            
            if not chunk_size:
                break
    
            offset += chunk_size
    
            print(offset, chunk.data_dict)        