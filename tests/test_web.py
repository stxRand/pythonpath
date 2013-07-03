import sys
import unittest
import webtest
from google.appengine.ext import testbed

from pythonpath.bestoffer import application


class TestApp(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(app_id='firstsuperhardtutotrial')
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_user_stub()

        self.testapp = webtest.TestApp(application)

    def tearDown(self):
        self.testbed.deactivate()

    def test_main_page(self):
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.content_type, 'text/html')
        self.assertIn('Product to comapre', response.normal_body)



