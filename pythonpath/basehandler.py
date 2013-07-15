import urllib
import decimal
import json
import webapp2

from webapp2_extras import jinja2
from google.appengine.api import users


def encode_url(tag, text):
    return urllib.urlencode({tag: text})


# from https://github.com/simplejson/simplejson/issues/34
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        jinja = jinja2.get_jinja2(app=self.app)
        jinja.environment.filters.update(dict(urlencode=urllib.quote))
        return jinja

    def render_response(self, _template, **context):
        # Renders a template and writes the result to the response.
        rv = self.jinja2.render_template(_template, **context)
        self.response.write(rv)

    def get_login_url_and_text(self, uri):
        url = ''
        url_linktext = ''
        if users.get_current_user():
            url = users.create_logout_url(uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(uri)
            url_linktext = 'Login'
        return (url, url_linktext)