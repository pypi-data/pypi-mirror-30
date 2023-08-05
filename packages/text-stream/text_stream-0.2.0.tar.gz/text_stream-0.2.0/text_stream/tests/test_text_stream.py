#!/usr/bin/env python3
"""
Test data is downloaded from
`github <https://github.com/georgeyumnam/quantum-espresso-codes/blob/master/2-Al/1_SCF/Al.pw.in>_`.
"""

import pathlib
import unittest

from text_stream import *


class TestText(unittest.TestCase):
    def setUp(self):
        self.file = 'data/Al.pw.in'
        with open(self.file) as f:
            self.text = f.read()

    def test_error(self):
        self.assertRaises(FileNotFoundError, TextStream, pathlib.Path('data/file_not_exists'))
