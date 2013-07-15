import datetime
import json

from google.appengine.api import users

import settings
from allegro import Allegro
from nokaut import Nokaut
from model import Search
from model import SearchCache
from basehandler import encode_url
from basehandler import BaseHandler
from basehandler import DecimalEncoder


class MainHandler(BaseHandler):

    def get(self):
        product_name = self.request.get('product', '')
        product_name = product_name.rstrip().lstrip()

        (url, url_linktext) = self.get_login_url_and_text(self.request.uri)

        user_nick = self.get_user_nickname()

        most_popular_search = SearchCache.get_most_popular_search(5)

        user_id = self.get_user_id()
        last_searches = Search.get_user_last_searches(user_id, 5)
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
        template_values.update(self.process_search(product_name))

        self.render_response('index.html', **template_values)

    def post(self):
        """
        Process search query. Return the result from search cache or
        send query to nokaut or allego.

        :param product: (str) The name of product to search for.

        :returns: (json dict)
            {
                'nokaut_price': nokaut_price,
                'nokaut_url': nokaut_url,
                'allegro_price': allegro_price,
                'allegro_url': allegro_url,
                'product': product
            }
        """

        product_name = self.request.get('product', '')
        result = self.process_search(product_name)
        result.update({'product': product_name})

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(result, cls=DecimalEncoder))

    def process_search(self, product_name):
        product_name = product_name.rstrip().lstrip()
        if (product_name != ''):
            allegro = Allegro()
            nokaut = Nokaut(nokaut_key=settings.NOKAUT_KEY)

            Search.add(product_name, users.get_current_user())

            cache_query = SearchCache.query(SearchCache.product_name == product_name)
            if (cache_query.count() > 0):
                cache = cache_query.fetch(1).pop()
                time_limit = datetime.datetime.now()-cache.insert_date
                if (time_limit.days > settings.DATABASE_EXPIRE_NUMBER_OF_DAYS):
                    # update
                    (allegro_price, allegro_url) = allegro.search(
                        "%s" % product_name)
                    (nokaut_price, nokaut_url) = nokaut.search(product_name)
                    cache.update(product_name, allegro_price, allegro_url,
                                 nokaut_price, nokaut_url)
                else:
                    # use previous results
                    allegro_price = cache.allegro_price
                    allegro_url = cache.allegro_url
                    nokaut_price = cache.nokaut_price
                    nokaut_url = cache.nokaut_url
                    cache.increment_search_count()
            else:
                # add
                (allegro_price, allegro_url) = allegro.search(
                    "%s" % product_name)
                (nokaut_price, nokaut_url) = nokaut.search(product_name)
                SearchCache.add(product_name,
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

    def get_user_id(self):
        user = users.get_current_user()
        user_id = None
        if (user is not None):
            user_id = user.user_id()
        return user_id

    def get_user_nickname(self):
        user = users.get_current_user()
        user_nick = ''
        if (user is not None):
            user_nick = user.nickname()
        return user_nick


class StorageHandler(BaseHandler):

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
