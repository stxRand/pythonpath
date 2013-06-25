import os

from google.appengine.api import users

import jinja2
import webapp2

from allegro import Allegro
from nokaut import Nokaut
import settings


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'])


def render_template(template, **params):
    template = JINJA_ENVIRONMENT.get_template(template)
    return template.render(params)


class MainPage(webapp2.RequestHandler):

    def get(self):

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'product': '',
            'url': url,
            'url_linktext': url_linktext,
        }

        self.response.write(render_template('index.html', **template_values))

class Compare(webapp2.RequestHandler):

    def get(self):
        product_name = self.request.get('product', '')

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        allegro = Allegro('"%s"'%product_name)
        allegro_price = allegro.get_lowest_price()
        allegro_url = allegro.get_offer_url()

        nokaut = Nokaut(product_name, settings.NOKAUT_KEY)
        nokaut_price = nokaut.get_lowest_price()
        nokaut_url = nokaut.get_offer_url()

        template_values = {
            'product_name': product_name,
            'nokaut_price': nokaut_price,
            'nokaut_url': nokaut_url,
            'allegro_price': allegro_price,
            'allegro_url': allegro_url,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/compare', Compare),
], debug=True)
