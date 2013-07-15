from google.appengine.ext import ndb

from decimal import Decimal


class DecimalProperty(ndb.StringProperty):
    def _validate(self, value):
        if not isinstance(value, (Decimal, str)):
            raise TypeError('expected decimal.Decimal, got %s' % repr(value))

    def _to_base_type(self, value):
        return str(value)

    def _from_base_type(self, value):
        return Decimal(value)

DEFAULT_SEARCH_KEY = 'Search'


class Search(ndb.Model):
    """Models an individual Search entry with author, query (product), and date.
    """

    author = ndb.UserProperty()
    product_name = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def default_parent_key(cls, author=None):
        """Constructs a default Datastore key for a Search Class."""

        if (author is None):
            return ndb.Key('Search', DEFAULT_SEARCH_KEY)
        else:
            return ndb.Key('Search', author)

    @classmethod
    def add(cls, product_name, user):
        user_id = user.user_id() if user else None
        search = Search(parent=Search.default_parent_key(user_id),
                        product_name=product_name)
        if user:
            search.author = user
        search.put()

    @classmethod
    def get_user_last_searches(cls, user_id, size):
        search_query = Search.query(
            ancestor=Search.default_parent_key(user_id)).order(-Search.date)
        return search_query.fetch(size)


class SearchCache(ndb.Model):
    """Model of search result cache"""
    product_name = ndb.StringProperty()
    insert_date = ndb.DateTimeProperty(auto_now_add=True)
    allegro_price = DecimalProperty()
    allegro_url = ndb.StringProperty()
    nokaut_price = DecimalProperty()
    nokaut_url = ndb.StringProperty()
    search_count = ndb.IntegerProperty()

    @classmethod
    def add(cls,
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
        return cache

    def update(self,
               product_name,
               allegro_price,
               allegro_url,
               nokaut_price,
               nokaut_url):
        self.product_name = product_name
        self.allegro_price = allegro_price
        self.allegro_url = allegro_url
        self.nokaut_price = nokaut_price
        self.nokaut_url = nokaut_url
        self.search_count = self.search_count+1
        self.put()

    def increment_search_count(self):
        if (self.search_count is None):
            self.search_count = 1
        self.search_count = self.search_count+1
        self.put()

    @classmethod
    def get_most_popular_search(cls, size):
        most_popular_query = SearchCache.query().order(-SearchCache.search_count)
        return most_popular_query.fetch(size)
