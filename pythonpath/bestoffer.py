import os
import urllib
import datetime

from google.appengine.api import users
import jinja2
import webapp2

import settings
from allegro import Allegro
from nokaut import Nokaut
from model import Search
from model import SearchCache

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'])
JINJA_ENVIRONMENT.filters.update(dict(urlencode = urllib.quote))


def render_template(template, **params):
    template = JINJA_ENVIRONMENT.get_template(template)
    return template.render(params)

def get_login_url_and_text(uri):
    url = ''
    url_linktext = ''
    if users.get_current_user():
        url = users.create_logout_url(uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(uri)
        url_linktext = 'Login'
    return (url, url_linktext)

def encode_url(tag, text):
    return urllib.urlencode({tag: text})


class MainPage(webapp2.RequestHandler):

    def get(self):

        (url, url_linktext) = get_login_url_and_text(self.request.uri)

        template_values = {
            'product': '',
            'url': url,
            'url_linktext': url_linktext,
        }

        self.response.write(render_template('index.html', **template_values))


class Compare(webapp2.RequestHandler):

    def get(self):
        product_name = self.request.get('product', '')
        product_name.rstrip().lstrip()

        (url, url_linktext) = get_login_url_and_text(self.request.uri)

        user_nick = self.__get_user_nickname()

        last_searches = self.__get_user_last_searches(5)
        self.__add_search(product_name)

        cache_query = SearchCache.query(SearchCache.product_name == product_name)
        if (cache_query.count() > 0):
            cache = cache_query.fetch(1).pop()
            time_limit = datetime.datetime.now()-cache.insert_date
            if (time_limit.days > settings.DATABASE_EXPIRE_NUMBER_OF_DAYS):
                # update
                (allegro_price, allegro_url) = \
                    self.__get_price_and_url_from_allegro(product_name)
                (nokaut_price, nokaut_url) = \
                    self.__get_price_and_url_from_nokaut(product_name)
                self.__update_search_cache(cache,
                                           product_name,
                                           allegro_price,
                                           allegro_url,
                                           nokaut_price,
                                           nokaut_url)
            else:
                # use previous results
                allegro_price = cache.allegro_price
                allegro_url = cache.allegro_url
                nokaut_price = cache.nokaut_price
                nokaut_url = cache.nokaut_url
        else:
            # add
            (allegro_price, allegro_url) = \
                self.__get_price_and_url_from_allegro(product_name)
            (nokaut_price, nokaut_url) = \
                self.__get_price_and_url_from_nokaut(product_name)
            self.__add_search_cache(product_name,
                                    allegro_price,
                                    allegro_url,
                                    nokaut_price,
                                    nokaut_url)
            pass

        last_searches_url = [encode_url('product', _search)
                             for _search in last_searches]
        template_values = {
            'product_name': product_name,
            'nokaut_price': nokaut_price,
            'nokaut_url': nokaut_url,
            'allegro_price': allegro_price,
            'allegro_url': allegro_url,
            'url': url,
            'url_linktext': url_linktext,
            'nick': user_nick,
            'last_searches': last_searches,
            'last_searches_url': last_searches_url
        }

        self.response.write(render_template('search.html', **template_values))

    def __get_user_id(self):
        user = users.get_current_user()
        user_id = None
        if (user is not None):
            user_id = user.user_id()
        return user_id

    def __get_user_nickname(self):
        user = users.get_current_user()
        user_nick = ''
        if (user is not None):
            user_nick = user.nickname()
        return user_nick

    def __get_user_last_searches(self, size):
        user_id = self.__get_user_id()
        search_query = Search.query(
            ancestor=Search.default_parent_key(user_id)).order(-Search.date)
        return search_query.fetch(size)

    def __add_search(self, product_name):
        user_id = self.__get_user_id()
        search = Search(parent=Search.default_parent_key(user_id),
                        product_name=product_name
                        )
        user = users.get_current_user()
        if user:
            search.author = user
        search.put()

    def __add_search_cache(self,
                           product_name,
                           allegro_price,
                           allegro_url,
                           nokaut_price,
                           nokaut_url):
        cache = SearchCache(product_name=product_name,
                            allegro_price=allegro_price,
                            allegro_url=allegro_url,
                            nokaut_price=nokaut_price,
                            nokaut_url=nokaut_url)
        cache.put()

    def __update_search_cache(self,
                              search_cache,
                              product_name,
                              allegro_price,
                              allegro_url,
                              nokaut_price,
                              nokaut_url):
        search_cache.product_name = product_name
        search_cache.allegro_price = allegro_price
        search_cache.allegro_url = allegro_url
        search_cache.nokaut_price = nokaut_price
        search_cache.nokaut_url = nokaut_url
        search_cache.put()

    def __get_price_and_url_from_allegro(self, product_name):
        allegro = Allegro('"%s"' % product_name)
        return (allegro.get_lowest_price(), allegro.get_offer_url())

    def __get_price_and_url_from_nokaut(self, product_name):
        nokaut = Nokaut(product_name, settings.NOKAUT_KEY)
        return (nokaut.get_lowest_price(), nokaut.get_offer_url())


class Storage(webapp2.RequestHandler):

    def get(self):

        (url, url_linktext) = get_login_url_and_text(self.request.uri)

        search_query = Search.query().order(-Search.date)
        search_query = search_query.fetch(10)

        template_values = {
            'searches': search_query,
            'url': url,
            'url_linktext': url_linktext,
        }

        self.response.write(render_template('storage.html', **template_values))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/compare', Compare),
    ('/storage', Storage)
], debug=True)
