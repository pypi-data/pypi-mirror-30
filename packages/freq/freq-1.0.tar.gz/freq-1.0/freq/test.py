#-*- coding: utf-8 -*-
import unittest
from freq import Freq

class TestMethods(unittest.TestCase):

    def test_initialize(self):
        country_codes = ["US", "US", "CA", "US"]
        freqs = Freq(country_codes)
        self.assertEqual(0.75, freqs["US"])
        self.assertEqual(0.25, freqs["CA"])
