import unittest
from mock import patch
import sys
from decimal import Decimal
from pythonpath.allegro import Allegro
from pythonpath.nokaut import Nokaut
from pythonpath import nokaut
from pythonpath import settings


class TestNokaut(unittest.TestCase):
    """testing nokaut module"""

    @patch.object(sys, 'argv', ['nokaut',
                                '-p', 'Sony nex-7',
                                '-k', settings.NOKAUT_KEY
                                ])
    def test_nokaut_main1(self):
        """testing nokaut class through main function"""

        try:
            nokaut.main()
        except Exception, err:
            self.fail('unexpected exception: %s' % err)

    @patch.object(sys, 'argv', ['nokaut', '-z'])
    def test_nokaut_main2(self):
        """testing nokaut class through main function"""

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
        """testing nokaut class through command line"""

        import os
        err = os.system(
            "nokaut -p 'Sony nex-7' -k '%s'" % settings.NOKAUT_KEY
        )
        self.assertEqual(err, 0)

        err = os.system(
            "nokaut -p 'Sony nex-7' -k '%s' -z" % settings.NOKAUT_KEY
        )
        self.assertNotEqual(err, 0)

        err = os.system(
            "nokaut -p 'Sony nex-7'"
        )
        self.assertNotEqual(err, 0)

        err = os.system(
            "nokaut -k '%s'" % settings.NOKAUT_KEY
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


class TestNokautClass(unittest.TestCase):
    """testing nokaut class"""

    def test_init(self):
        nokaut = Nokaut('')
        self.assertIsInstance(nokaut, Nokaut)

    def test_search(self):
        """testing nokaut class offer search"""

        nokaut_search = Nokaut('Aparat Sony nex-7', settings.NOKAUT_KEY)
        price = nokaut_search.get_lowest_price()
        url = nokaut_search.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertTrue(price >= Decimal(0.0))
        self.assertIsInstance(url, str)
        self.assertNotEqual(url, '')

    def test_empty_search(self):
        """testing nokaut class offer empty string search"""

        nokaut = Nokaut('', settings.NOKAUT_KEY)
        price = nokaut.get_lowest_price()
        url = nokaut.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertTrue(price >= Decimal(0.0))
        self.assertIsInstance(url, str)


class TestAllegroClass(unittest.TestCase):
    """testing allegro class"""

    def test_init(self):
        allegro = Allegro('')
        self.assertIsInstance(allegro, Allegro)

    def test_search(self):
        """testing allegro class offer search"""

        allegro = Allegro('"Aparat Sony nex-7"')
        price = allegro.get_lowest_price()
        url = allegro.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertTrue(price >= Decimal(0.0))
        self.assertIsInstance(url, str)
        self.assertNotEqual(url, '')

    def test_empty_search(self):
        """testing allegro class offer empty string search"""

        allegro = Allegro('')
        price = allegro.get_lowest_price()
        url = allegro.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertTrue(price >= Decimal(0.0))
        self.assertIsInstance(url, str)


if __name__ == '__main__':
    unittest.main()
