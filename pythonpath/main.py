import os
import webapp2
from view import MainHandler
from view import StorageHandler
from view import AllegroThumbHandler
from view import AllegroImageHandler
from view import NokautThumbHandler
from view import NokautImageHandler

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'templates'
    ),
}

application = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/storage', StorageHandler),
    ('/image/allegro', AllegroImageHandler),
    ('/image/allegro/thumb', AllegroThumbHandler),
    ('/image/nokaut', NokautImageHandler),
    ('/image/nokaut/thumb', NokautThumbHandler)
], debug=True, config=config)
