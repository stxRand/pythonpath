import unittest
import webtest
from google.appengine.ext import testbed
from mock import patch
from decimal import Decimal
import json

from pythonpath.bestoffer import application


class TestApp(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(app_id='firstsuperhardtutotrial')
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()
        self.testbed.init_memcache_stub()

        self.testapp = webtest.TestApp(application)

    def tearDown(self):
        self.testbed.deactivate()

    def test_main_page(self):
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'text/html')
        self.assertIn('Product to comapre', response.normal_body)

    @patch('urllib2.urlopen')
    @patch('pythonpath.allegro.Allegro.get_img_url')
    @patch('pythonpath.allegro.Allegro.get_offer_url')
    @patch('pythonpath.allegro.Allegro.get_lowest_price')
    @patch('pythonpath.allegro.Allegro.search')
    @patch('pythonpath.nokaut.Nokaut.get_img_url')
    @patch('pythonpath.nokaut.Nokaut.get_offer_url')
    @patch('pythonpath.nokaut.Nokaut.get_lowest_price')
    @patch('pythonpath.nokaut.Nokaut.search')
    def test_main_post(self,
                       mock_nokaut_search,
                       mock_nokaut_get_lowest_price,
                       mock_nokaut_get_offer_url,
                       mock_nokaut_get_img_url,
                       mock_allegro_search,
                       mock_allegro_get_lowest_price,
                       mock_allegro_get_offer_url,
                       mock_allegro_get_img_url,
                       mock_urllib):
        import StringIO
        mock_urllib.return_value = StringIO.StringIO('')

        mock_allegro_search.return_value = (Decimal(100.0), 'www.allegro.pl')
        mock_allegro_get_lowest_price.return_value = Decimal(100.0)
        mock_allegro_get_offer_url.return_value = 'www.allegro.pl'
        mock_allegro_get_img_url.return_value = ''

        mock_nokaut_search.return_value = (Decimal(200.0), 'www.nokaut.pl')
        mock_nokaut_get_lowest_price.return_value = Decimal(200.0)
        mock_nokaut_get_offer_url.return_value = 'www.nokaut.pl'
        mock_nokaut_get_img_url.return_value = ''

        param = {'product': 'anything'}
        response = self.testapp.post('/', param)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.headers['Content-type'], 'application/json')
        response_body = json.loads(response.body)
        self.assertEqual(response_body['allegro_price'], unicode(Decimal(100.0)))
        self.assertEqual(response_body['nokaut_price'], unicode(Decimal(200.0)))
        self.assertEqual(response_body['allegro_url'], 'www.allegro.pl')
        self.assertEqual(response_body['nokaut_url'], 'www.nokaut.pl')

    def test_search_cache(self):
        from pythonpath.model import SearchCache
        SearchCache.add('Book', Decimal(100.0), 'www.allegro.pl',
                        Decimal(200.0), 'www.nokaut.pl')
        SearchCache.add('Tree', Decimal(100.0), 'www.allegro.pl',
                        Decimal(200.0), 'www.nokaut.pl')

        self.assertEqual(2, SearchCache.query().count())

        book = SearchCache.find_product('Book').fetch(1)[0]
        book.update('Book', Decimal(100.0), 'www.allegro.pl/test',
                    Decimal(300.0), 'www.nokaut.pl')

        self.assertEqual('Book', book.product_name)
        self.assertEqual(Decimal(100.0), book.allegro_price)
        self.assertEqual('www.allegro.pl/test', book.allegro_url)
        self.assertEqual(Decimal(300.0), book.nokaut_price)
        self.assertEqual('www.nokaut.pl', book.nokaut_url)
        self.assertEqual(2, book.search_count)


if __name__ == '__main__':
    unittest.main()
