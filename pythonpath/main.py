import os
import webapp2
from view import MainHandler
from view import StorageHandler

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'templates'
    ),
}

application = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/storage', StorageHandler)
], debug=True, config=config)
