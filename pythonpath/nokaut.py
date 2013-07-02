import urllib2
import urllib
from lxml import etree
import sys
import argparse
import logging
from decimal import Decimal

from offer_provider import OfferProvider


logging.basicConfig(filename='pythonpath.log', level=logging.DEBUG)


class Nokaut(OfferProvider):
    """The class allow to search for a product in the nokaut.pl
    with the lowest price"""

    def __init__(self, product_name='', nokaut_key=''):
        self.product_name = product_name
        self.nokaut_key = nokaut_key
        self._price = Decimal(0.0)
        self._url = ''

    def search(self, product_name=None):
        """Finds a offer of product with the lowest price in the
        nokaut.pl portal. It returns a tuple with lowest price and a url to
        nokaut.pl product web site.

        :param product_name: The name of product to search for in nokaut.pl.
        :type product_name: str.
        :returns: (Decimal,str) -- the lowest price of product and url to
        nokaut product site.

        """

        if (product_name is not None):
            self.product_name = product_name

        xml = self.__get_xml_with_nokaut_api(
            'nokaut.Price.getByProductName',
            'name',
            self.product_name
        )
        (product_id, self._price, shop_url) = \
            self.__get_productid_price_and_url(xml)

        xml = self.__get_xml_with_nokaut_api(
            'nokaut.Product.getById', 'id', product_id
        )
        self._url = self.__get_product_url(xml)

        logging.debug((self._price, self._url))

        return (self._price, self._url)

    def get_lowest_price(self):
        """Returns the lowest price from the last search"""

        return self._price

    def get_offer_url(self):
        """Returns a product url from the last search"""

        return self._url

    def __get_xml_with_nokaut_api(self, method,
                                  method_param_name,
                                  method_param_value):
        url_params = {
            'format': 'xml',
            'key': self.nokaut_key,
            'method': method,
            method_param_name: method_param_value
        }
        url_params = urllib.urlencode(url_params)

        nokaut_url = 'http://api.nokaut.pl/?%s' % url_params
        response = urllib2.urlopen(nokaut_url)
        return response.read()

    def __get_productid_price_and_url(self, xml):
        products = {}
        price = Decimal(0.0)
        shop_url = ''
        product_id = 0

        xml = etree.fromstring(xml)
        for item in xml.xpath(".//item"):
            price = item.findtext("price").replace(',', '.')
            price = Decimal(price)
            product_id = int(item.findtext("product_id"))
            shop_url = str(item.findtext("shop_url"))
            (tmp_price, tmp_shop_url) = \
                products.setdefault(product_id, (price, shop_url))
            if (price < tmp_price):
                products[product_id] = (price, shop_url)

        logging.debug(products)
        if (len(products) == 0):
            return ('', Decimal(0.0), '')
        (product_id, price_and_url) = products.popitem()
        return (product_id, price_and_url[0], price_and_url[1])

    def __get_product_url(self, xml):
        xml = etree.fromstring(xml)
        url = ''
        for product_url in xml.xpath(".//url/text()"):
            url = str(product_url)
        logging.debug(url)
        return url


class ArgumentParserHelpError(argparse.ArgumentParser):
    def print_help(self, file=None):
        super(ArgumentParserHelpError, self).print_help(file)
        sys.exit(1)


def main():
    parser = ArgumentParserHelpError(
        description='Get the best offer from Nokaut.'
    )
    parser.add_argument('-p', '--product', type=str,
                        help='name of a product to search', required=True)
    parser.add_argument('-k', '--key', type=str,
                        help='nokaut partnership key', required=True)
    args = parser.parse_args()

    try:
        nokaut_search = Nokaut(product_name=args.product, nokaut_key=args.key)
        (price, url) = nokaut_search.search()
        print(price, url)
    except argparse.ArgumentError, err:
        print(err.message)
        sys.exit(2)


if __name__ == "__main__":
    main()
