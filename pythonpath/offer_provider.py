import abc
from decimal import Decimal


class OfferProvider(object):
    """Ofer Provider interface"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def search(self, product_name=None):
        """Finds a offer of product with the lowest price in the
        offer provider. It returns a tuple with lowest price and a url to
        the offer.

        :param product_name: The name of product to search.
        :type product_name: str.
        :returns: (Decimal,str) -- the lowest price of product and url to the shop.

        """

        return (Decimal(0.0), '')

    @abc.abstractproperty
    def get_lowest_price(self):
        """Returns the lowest price from the last search"""
        return Decimal(0.0)

    @abc.abstractproperty
    def get_offer_url(self):
        """Returns a offer url from the last search"""
        return ''
