import sys
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
from lib import nokaut

import unittest

class TestNokaut(unittest.TestCase):

    def test_nokaut(self):
        (price, url) = nokaut.nokaut(product_name='Sony nex-7', nokaut_key='bad_key')
        self.assertIsNone(price)
        (price, url) = nokaut.nokaut(product_name='Sony nex-7', nokaut_key='a8839b1180ea00fa1cf7c6b74ca01bb5')
        self.assertTrue(price >= 0.0)
        self.assertIsInstance(price, float)
        self.assertIsInstance(url, str)

if __name__ == '__main__':
    unittest.main()
