import urllib
import datetime
import os

from google.appengine.api import users

import webapp2
from webapp2_extras import jinja2

import settings
from allegro import Allegro
from nokaut import Nokaut
from model import Search
from model import SearchCache


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


def encode_url(tag, text):
    return urllib.urlencode({tag: text})


class MainPage(BaseHandler):

    def get(self):

        most_popular_search = self.__get_most_popular_search(5)

        product_name = self.request.get('product', '')
        product_name = product_name.rstrip().lstrip()

        (url, url_linktext) = self.get_login_url_and_text(self.request.uri)

        user_nick = self.__get_user_nickname()

        last_searches = self.__get_user_last_searches(5)
        last_searches_url = [encode_url('product', _search)
                             for _search in last_searches]

        template_values = {
            'product_name': product_name,
            'url': url,
            'url_linktext': url_linktext,
            'nick': user_nick,
            'last_searches': last_searches,
            'last_searches_url': last_searches_url,
            'most_popular_search': most_popular_search
        }
        template_values.update(self.__process_search(product_name))

        self.render_response('index.html', **template_values)

    def __process_search(self, product_name):
        if (product_name != ''):
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
                    self.__increment_search_count(cache)
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
            return {
                'nokaut_price': nokaut_price,
                'nokaut_url': nokaut_url,
                'allegro_price': allegro_price,
                'allegro_url': allegro_url
            }
        else:
            return {}

    def __get_most_popular_search(self, size):
        most_popular_query = SearchCache.query().order(-SearchCache.search_count)
        return most_popular_query.fetch(size)

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
                            nokaut_url=nokaut_url,
                            search_count=1)
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
        search_cache.search_count = search_cache.search_count+1
        search_cache.put()

    def __increment_search_count(self, search_cache):
        if (search_cache.search_count is None):
            search_cache.search_count = 1
        search_cache.search_count = search_cache.search_count+1
        search_cache.put()

    def __get_price_and_url_from_allegro(self, product_name):
        allegro = Allegro('"%s"' % product_name)
        return allegro.search()

    def __get_price_and_url_from_nokaut(self, product_name):
        nokaut = Nokaut(product_name, settings.NOKAUT_KEY)
        return nokaut.search()


class Storage(BaseHandler):

    def get(self):

        (url, url_linktext) = self.get_login_url_and_text(self.request.uri)

        search_query = Search.query().order(-Search.date)
        search_query = search_query.fetch(10)

        template_values = {
            'searches': search_query,
            'url': url,
            'url_linktext': url_linktext,
        }

        self.render_response('storage.html', **template_values)

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'templates'
    ),
}
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/storage', Storage)
], debug=True, config=config)
