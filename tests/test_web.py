import unittest
import webtest
from google.appengine.ext import testbed
from mock import patch
from decimal import Decimal
import json

from pythonpath.bestoffer import application
from pythonpath.bestoffer import DecimalEncoder


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

    @patch('pythonpath.allegro.Allegro.search')
    @patch('pythonpath.nokaut.Nokaut.search')
    def test_main_post(self, mock_nokaut, mock_allegro):
        mock_allegro.return_value = (Decimal(100.0), 'www.allegro.pl')
        mock_nokaut.return_value = (Decimal(200.0), 'www.nokaut.pl')

        param = {'product': 'anything'}
        response = self.testapp.post('/', param)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.headers['Content-type'], 'application/json')
        response_body = json.loads(response.body)
        self.assertEqual(response_body['allegro_price'], unicode(Decimal(100.0)))
        self.assertEqual(response_body['nokaut_price'], unicode(Decimal(200.0)))
        self.assertEqual(response_body['allegro_url'], 'www.allegro.pl')
        self.assertEqual(response_body['nokaut_url'], 'www.nokaut.pl')


if __name__ == '__main__':
    unittest.main()
