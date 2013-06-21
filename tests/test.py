import unittest
from mock import patch
import sys
from pythonpath import nokaut
from decimal import Decimal


class TestNokaut(unittest.TestCase):

    def test_nokaut(self):
        """testing get_proce_and_url_from_nokaut function from nokaut"""

        (price, url) = nokaut.get_proce_and_url_from_nokaut(
            product_name='Sony nex-7',
            nokaut_key='bad_key'
        )
        self.assertIsNone(price)
        (price, url) = nokaut.get_proce_and_url_from_nokaut(
            product_name='Sony nex-7',
            nokaut_key='a8839b1180ea00fa1cf7c6b74ca01bb5'
        )
        self.assertIsInstance(price, Decimal)
        self.assertTrue(price >= 0.0)
        self.assertIsInstance(url, str)

    @patch.object(sys, 'argv', ['nokaut',
                                '-p', 'Sony nex-7',
                                '-k', 'a8839b1180ea00fa1cf7c6b74ca01bb5'
                                ])
    def test_nokaut_main1(self):
        """testing get_proce_and_url_from_nokaut
        function through main function

        """

        try:
            nokaut.main()
        except Exception, err:
            self.fail('unexpected exception: %s' % err)

    @patch.object(sys, 'argv', ['nokaut', '-z'])
    def test_nokaut_main2(self):
        """testing get_proce_and_url_from_nokaut 
        function through main function

        """

        try:
            nokaut.main()
        except SystemExit, err:
            self.assertEquals(type(err), type(SystemExit()))
            self.assertEquals(err.code, 2)
        except Exception, err:
            self.fail('unexpected exception: %s' % err)
        else:
            self.fail('SystemExit exception expected')

    @patch.object(sys, 'argv', ['nokaut', '-h'])
    def test_nokaut_main3(self):
        try:
            nokaut.main()
        except SystemExit, err:
            self.assertEquals(type(err), type(SystemExit()))
            self.assertEquals(err.code, 1)
        except Exception, err:
            self.fail('unexpected exception: %s' % err)
        else:
            self.fail('SystemExit exception expected')

    def test_nokaut_commandline(self):
        """testing get_proce_and_url_from_nokaut 
        function through command line

        """
        
        import os
        err = os.system(
            "nokaut -p 'Sony nex-7' -k 'a8839b1180ea00fa1cf7c6b74ca01bb5'"
        )
        self.assertEqual(err, 0)

        err = os.system(
            "nokaut -p 'Sony nex-7' -k 'a8839b1180ea00fa1cf7c6b74ca01bb5' -z"
        )
        self.assertNotEqual(err, 0)

        err = os.system(
            "nokaut -p 'Sony nex-7'"
        )
        self.assertNotEqual(err, 0)

        err = os.system(
            "nokaut -k 'a8839b1180ea00fa1cf7c6b74ca01bb5'"
        )
        self.assertNotEqual(err, 0)

        err = os.system(
            "nokaut -h"
        )
        self.assertNotEqual(err, 0)

        err = os.system(
            "nokaut -z"
        )
        self.assertNotEqual(err, 0)


if __name__ == '__main__':
    unittest.main()
