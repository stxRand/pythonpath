import datetime
import json
import urllib2
import webapp2

from google.appengine.api import users

import settings
from allegro import Allegro
from nokaut import Nokaut
from model import Search
from model import SearchCache
from basehandler import encode_url
from basehandler import BaseHandler
from basehandler import DecimalEncoder

import logging
logging.basicConfig(filename='pythonpath.log', level=logging.DEBUG)

class MainHandler(BaseHandler):

    def get(self):
        product_name = self.request.get('product', '')
        product_name = product_name.rstrip().lstrip()

        (url, url_linktext) = self.get_login_url_and_text(self.request.uri)

        user_nick = self.get_user_nickname()

        most_popular_search = SearchCache.get_most_popular_search(5)

        user_id = self.get_user_id()
        last_searches = Search.fetch_user_last_searches(user_id, 5)
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
            image_id = -1

            Search.add(product_name, users.get_current_user())

            cache_query = SearchCache.find_product(product_name)
            if (cache_query.count() > 0):
                cache = cache_query.fetch(1).pop()
                time_limit = datetime.datetime.now()-cache.insert_date
                if (time_limit.days > settings.DATABASE_EXPIRE_NUMBER_OF_DAYS):
                    # update
                    allegro.search("%s" % product_name)
                    allegro_price = allegro.get_lowest_price()
                    allegro_url = allegro.get_offer_url()
                    allegro_img_url = allegro.get_img_url()
                    allegro_img = urllib2.urlopen(allegro_img_url).read()

                    nokaut.search(product_name)
                    nokaut_price = nokaut.get_lowest_price()
                    nokaut_url = nokaut.get_offer_url()
                    nokaut_img_url = nokaut.get_img_url()
                    nokaut_img = urllib2.urlopen(nokaut_img_url).read()
                    cache.update(product_name, allegro_price, allegro_url,
                                 nokaut_price, nokaut_url,
                                 allegro_img, nokaut_img)
                    image_id = cache.key.id()
                else:
                    # use previous results
                    allegro_price = cache.allegro_price
                    allegro_url = cache.allegro_url
                    nokaut_price = cache.nokaut_price
                    nokaut_url = cache.nokaut_url
                    cache.increment_search_count()
                    image_id = cache.key.id()
            else:
                # add
                allegro.search("%s" % product_name)
                allegro_price = allegro.get_lowest_price()
                allegro_url = allegro.get_offer_url()
                allegro_img_url = allegro.get_img_url()
                allegro_img = urllib2.urlopen(allegro_img_url).read()

                nokaut.search(product_name)
                nokaut_price = nokaut.get_lowest_price()
                nokaut_url = nokaut.get_offer_url()
                nokaut_img_url = nokaut.get_img_url()
                nokaut_img = urllib2.urlopen(nokaut_img_url).read()
                cache = SearchCache.add(product_name,
                                        allegro_price,
                                        allegro_url,
                                        nokaut_price,
                                        nokaut_url,
                                        allegro_img,
                                        nokaut_img)
                image_id = cache.key.id()
            return {
                'nokaut_price': nokaut_price,
                'nokaut_url': nokaut_url,
                'allegro_price': allegro_price,
                'allegro_url': allegro_url,
                'image_id': image_id,
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

        search_query = Search.fetch_last_searches(10)

        template_values = {
            'searches': search_query,
            'url': url,
            'url_linktext': url_linktext,
        }

        self.render_response('storage.html', **template_values)


class AllegroThumbHandler(webapp2.RequestHandler):
    def get(self):
        id = self.request.get("id")
        if id:
            photo = SearchCache.get_allegro_thumb(int(id))
            if photo is not None:
                self.response.headers['Content-Type'] = 'image/jpeg'
                self.response.out.write(photo)
                return
        self.error(404)


class AllegroImageHandler(webapp2.RequestHandler):
    def get(self):
        id = self.request.get("id")
        if id:
            photo = SearchCache.get_allegro_image(int(id))
            if photo is not None:
                self.response.headers['Content-Type'] = 'image/jpeg'
                self.response.out.write(photo)
                return
        self.error(404)


class NokautThumbHandler(webapp2.RequestHandler):
    def get(self):
        id = self.request.get("id")
        if id:
            photo = SearchCache.get_nokaut_thumb(int(id))
            if photo is not None:
                self.response.headers['Content-Type'] = 'image/jpeg'
                self.response.out.write(photo)
                return
        self.error(404)


class NokautImageHandler(webapp2.RequestHandler):
    def get(self):
        id = self.request.get("id")
        if id:
            photo = SearchCache.get_nokaut_image(int(id))
            if photo is not None:
                self.response.headers['Content-Type'] = 'image/jpeg'
                self.response.out.write(photo)
                return
        self.error(404)
