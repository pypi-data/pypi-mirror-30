# -*- coding: utf-8 -*-

###############################################################################
import os
import unittest
from hexer.hexer import Hexer

###############################################################################
class TestHexDump(unittest.TestCase):

    def test_hexdump(self):
        filename = os.path.join('data', 'w699.0')
        hexer = Hexer(filename)
        
        # full dump
        hexer.hexdump(output=False)

        # only part from file
        hexer.hexdump(size=512)

        # with offset
        hexer.hexdump(offset=128, size=512)

        # from tail
        hexer.hexdump(offset=-128, size=512)
        
