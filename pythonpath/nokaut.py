import urllib2
import urllib
from lxml import etree
import sys
import getopt
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
        context = self.__get_xml_iter_context(
            xml,
            tag_list=('item', 'price', 'product_id',
                      'shop_url')
        )

        (product_id, self._price, shop_url) = \
            self.__get_poduct_id_price_shop_url_from_xml_context(context)

        xml = self.__get_xml_with_nokaut_api(
            'nokaut.Product.getById',
            'id',
            product_id
        )
        context = self.__get_xml_iter_context(xml,
                                              tag_list=('item', 'url'))
        self._url = self.__get_product_url_form_xml_context(context)

        logging.debug((self._price, self._url))

        return (self._price, self._url)

    def get_lowest_price(self):
        "Returns the lowest price from the last search"

        return self._price

    def get_offer_url(self):
        "Returns a product url from the last search"

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

    def __get_xml_iter_context(self, xml, tag_list):
        root = etree.XML(xml)
        return etree.iterwalk(root, events=("start", "end"),
                              tag=tag_list)

    def __get_poduct_id_price_shop_url_from_xml_context(self, context):
        products = {}
        price = Decimal(0.0)
        shop_url = ''
        product_id = 0

        for action, elem in context:
            if (action == 'end'):
                if (elem.tag == 'item'):
                    (old_price, old_shop_url) = products.setdefault(product_id,
                                                                    (price, shop_url))
                    if (price < old_price):
                        products[product_id] = (price, shop_url)
                elif (elem.tag == 'price'):
                    price = Decimal(elem.text.replace(',', '.'))
                elif (elem.tag == 'product_id'):
                    product_id = int(elem.text)
                elif (elem.tag == 'shop_url'):
                    shop_url = str(elem.text)

        logging.debug(products)
        if (len(products) == 0):
            return (None, None, None)
        (product_id, price_and_url) = products.popitem()
        return (product_id, price_and_url[0], price_and_url[1])

    def __get_product_url_form_xml_context(self, context):
        for action, elem in context:
            if (action == 'end' and elem.tag == 'url'):
                return str(elem.text)
        return ''


def usage():
    "usage of the command line"

    print("nokaut -p 'product_name' -k 'your_nokaut_key'")


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hp:k:", ["help", "product=", "key="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    key = None
    product = None

    for opt, arg in opts:
        if (opt in ("-h", "--help")):
            usage()
            sys.exit(1)
        elif (opt in ("-p", "--product")):
            product = arg
        elif (opt in ("-k", "--key")):
            key = arg
        else:
            usage()
            sys.exit(2)

    if (key is None or product is None):
        usage()
        sys.exit(2)
    else:
        nokaut_search = Nokaut(product_name=product, nokaut_key=key)
        (price, url) = nokaut_search.search()
        print(price, url)


if __name__ == "__main__":
    main()
