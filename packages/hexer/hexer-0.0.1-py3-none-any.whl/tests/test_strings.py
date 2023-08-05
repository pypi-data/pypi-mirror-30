# -*- coding: utf-8 -*-

###############################################################################
import os
import re
import unittest
from hexer.hexer import Hexer

###############################################################################
class TestStrings(unittest.TestCase):

    def test_strings(self):
        filename = os.path.join('data', 'w699.0')
    
        hexer = Hexer(filename)
        offsets, strings = hexer.strings(min_len=3)

        keywords = [
                'AQM', 'APF', 'APT', 'ASS', 'BBW', 'BFW', 'BMS', 'CNM', 'COR',
                'DAQ', 'DAT', 'DEL', 'DLY', 'DTC', 'DXU', 'FOC', 'FXV', 'GBW',
                'HFL', 'HFQ', 'HFW', 'HPF', 'INS', 'LPF', 'LXV', 'LWN', 'MIN',
                'MVD', 'NPT', 'NSS', 'PGN', 'PHZ', 'SFM', 'SGN', 'SG2', 'SNM',
                'SON', 'SRC', 'SRN', 'TIM', 'VEL', 'ZFF']

        found_keywords = set()
        
        for s in strings:
            if len(s) == 3:
                match = re.search('^[A-Z][A-Z][A-Z0-9]', s)
        
                if match:
                    found_keywords.add(s)
                    
        for k in keywords:
            self.assertTrue(k in found_keywords)
            # found_keywords.remove(k)

        # print(sorted(found_keywords))

        ### strings
        self.assertTrue('09/03/2018' in strings)
        self.assertTrue('13:45:16.309 (UTC+1)' in strings)
        self.assertTrue('2109' in strings)
        self.assertTrue('2 mm' in strings)
        self.assertTrue('KBr' in strings)
        self.assertTrue('LN-MCT Mid [Internal Pos.2]' in strings)
        self.assertTrue('Right Input' in strings)
        self.assertTrue('Sample Compartment' in strings)
        self.assertTrue('VERTEX 70' in strings)
