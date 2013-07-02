import unittest
from mock import patch
import sys
from decimal import Decimal
from StringIO import StringIO

from pythonpath.allegro import Allegro
from pythonpath.nokaut import Nokaut
from pythonpath import nokaut
from pythonpath import settings

import static


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


def mock_urlopen_function(url):
    if (not isinstance(url, str)):
        url = url.get_full_url()
    url = str(url)
    if ('allegro.pl' in url and not 'string=&' in url):
        if('description=1' in url
           and 'order=p' in url
           and 'standard_allegro=1' in url
           and 'offerTypeBuyNow=1' in url
          ):
            return MockUrlOpen(static.SEARCH_ALLEGRO_APARAT_SONY_NEX_7_WITH_ORDER, url)
        return MockUrlOpen(static.SEARCH_ALLEGRO_APARAT_SONY_NEX_7, url)
    elif('api.nokaut.pl' in url):
        if('name=&' in url and
            'method=nokaut.Price.getByProductName' in url and
            'key=' in url and
            'format=xml' in url
           ):
            return MockUrlOpen(static.GET_EMPTY_NOKAUT_RESPONSE,url)
        elif ('name=' in url and
            'method=nokaut.Price.getByProductName' in url and
            'key=' in url and
            'format=xml' in url
           ):
            return MockUrlOpen(static.GET_PRICE_NOKAUT_RESPONSE, url)
        elif ('id=&' in url and
            'method=nokaut.Product.getById' in url and
            'key=' in url and
            'format=xml' in url
           ):
            return MockUrlOpen(static.GET_EMPTY_NOKAUT_RESPONSE,url)
        elif ('id=' in url and
            'method=nokaut.Product.getById' in url and
            'key=' in url and
            'format=xml' in url
           ):
            return MockUrlOpen(static.GET_PRODUCT_NOKAUT_RESPONSE, url)
        else:
            MockUrlOpen('', url)
    return MockUrlOpen('', url)


class TestNokautClass(unittest.TestCase):
    """testing nokaut class"""

    def test_search(self):
        """testing nokaut class offer search"""

        nokaut_search = Nokaut('Aparat Sony nex-7', settings.NOKAUT_KEY)
        nokaut_search.search()
        price = nokaut_search.get_lowest_price()
        url = nokaut_search.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertTrue(price >= Decimal(0.0))
        self.assertIsInstance(url, str)
        self.assertNotEqual(url, '')

    @patch('urllib2.urlopen', mock_urlopen_function)
    def test_search_offline(self):
        """testing nokaut class offer search"""

        nokaut_search = Nokaut('Aparat Sony nex-7', settings.NOKAUT_KEY)
        nokaut_search.search()
        price = nokaut_search.get_lowest_price()
        url = nokaut_search.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertEqual(price, Decimal(3699.00))
        self.assertIsInstance(url, str)
        self.assertEqual(url, 'http://www.nokaut.pl/aparaty-cyfrowe/sony-nex-7.html')

    def test_empty_search(self):
        """testing nokaut class offer empty string search"""

        nokaut = Nokaut('', settings.NOKAUT_KEY)
        nokaut.search()
        price = nokaut.get_lowest_price()
        url = nokaut.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertTrue(price >= Decimal(0.0))
        self.assertIsInstance(url, str)

    @patch('urllib2.urlopen', mock_urlopen_function)
    def test_empty_search_offline(self):
        """testing nokaut class offer empty string search"""

        nokaut = Nokaut('', settings.NOKAUT_KEY)
        nokaut.search()
        price = nokaut.get_lowest_price()
        url = nokaut.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertEqual(price, Decimal(0.0))
        self.assertIsInstance(url, str)
        self.assertEqual(url, '')


class TestAllegroClass(unittest.TestCase):
    """testing allegro class"""

    def test_search(self):
        """testing allegro class offer search"""

        allegro = Allegro('"Aparat Sony nex-7"')
        allegro.search()
        price = allegro.get_lowest_price()
        url = allegro.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertTrue(price >= Decimal(0.0))
        self.assertIsInstance(url, str)
        self.assertNotEqual(url, '')

    def test_empty_search(self):
        """testing allegro class offer empty string search"""

        allegro = Allegro('')
        allegro.search()
        price = allegro.get_lowest_price()
        url = allegro.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertTrue(price >= Decimal(0.0))
        self.assertIsInstance(url, str)

    @patch('mechanize.urlopen', mock_urlopen_function)
    def test_search_offline(self):
        """testing allegro class offer search offilne"""

        allegro = Allegro('"Aparat Sony nex-7"')
        allegro.search()
        price = allegro.get_lowest_price()
        url = allegro.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertTrue(price == Decimal(4275.00))
        self.assertIsInstance(url, str)
        self.assertEqual(
            url,
            'http://www.allegro.pl/aparat-sony-nex-7-18-55mm-16gb-' + 
            'etui-nowosc-wa-ss-i3358538364.html'
        )

    @patch('mechanize.urlopen', mock_urlopen_function)
    def test_empty_search_offline(self):
        """testing allegro class offer empty string search"""

        allegro = Allegro('')
        allegro.search()
        price = allegro.get_lowest_price()
        url = allegro.get_offer_url()

        self.assertIsInstance(price, Decimal)
        self.assertTrue(price == Decimal(0.0))
        self.assertIsInstance(url, str)
        self.assertEqual(url, '')


class MockUrlOpen(StringIO):

    def __init__(self, buffer_=None, url=''):
        StringIO.__init__(self, buffer_)
        self.url = url

    def geturl(self):
        return self.url

    def info(self):
        return ''

    def getcode(self):
        return ''


if __name__ == '__main__':
    unittest.main()
