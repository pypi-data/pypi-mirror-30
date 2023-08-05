# Copyright (c) 2017 Thomas Thurman
# See LICENSE.txt for details.

import unittest

EXPECTED = {
   ('TKPWHREPB',): 'glen',
   ('A',): 'a',
   ('TK*EB', 'TK*EB', 'R-R'):
        # no, I don't know why; it was in the sample dct
        '"Debbie \'Do Anything for Hillary\' Wasserman Schultz"',
   ('TKEUGZ', 'AER'):
        'dictionary',
   ('HAOER',): 'here',
   ('SEZ',): 'says',
   ('S',): 'is',
   ('SKW-FRPBLGTS',): '{^{A}And}',
   ('STKPWHRAEPBG',): '{^{Q}What, if anything,^}',
   ('SPHAUL',): 'small',
}

from plover_digitalcat_dictionary import DigitalCATDictionary

class TestCase(unittest.TestCase):

    def test_load_dictionary(self):

        # this test can produce useful output if it fails
        self.maxDiff = None

        filename = 'test/digitalcat-test.dct'
        d = DigitalCATDictionary.load(filename)

        for stroke, english in sorted(EXPECTED.items()):
            self.assertEqual(d[stroke], english)
