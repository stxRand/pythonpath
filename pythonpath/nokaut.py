import urllib2
import urllib
from lxml import etree
import sys
import getopt
from decimal import Decimal
import logging


logging.basicConfig(filename='pythonpath.log', level=logging.DEBUG)


def get_price_and_url_from_nokaut(product_name='', nokaut_key=''):
    """This function finds the lowest price offer of the product
    and url of the shop from nokaut.pl. it is neccessary to have nokaut.pl
    partnership key.

    :param product_name: The name of product to search for in nokaut.pl.
    :type product_name: str.
    :param nokaut_key: nokaut.pl partnership key.
    :type nokaut_key: str.
    :returns: (Decimal,str) -- the lowest price of product and url to the shop.

    """
    method = 'nokaut.Price.getByProductName'
    method_param = 'name'

    url_params = {'format': 'xml', 'key': nokaut_key, 'method': method,
                  method_param: product_name, 'sortDirection': 'price'}
    url_params = urllib.urlencode(url_params)

    nokaut_url = 'http://api.nokaut.pl/?%s' % url_params
    response = urllib2.urlopen(nokaut_url)
    xml = response.read()
    root = etree.XML(xml)
    context = etree.iterwalk(root, events=("start", "end"),
                             tag=('item', 'price', 'product_id', 'shop_url'))

    products = {}
    price = Decimal(0.0)
    shop_url = ''
    product_id = 0

    for action, elem in context:
        if (action == 'end' and elem.tag == 'item'):
            (old_price, old_shop_url) = products.setdefault(product_id,
                                                            (price, shop_url))
            if (price < old_price):
                products[product_id] = (price, shop_url)
        if (action == 'end' and elem.tag == 'price'):
            price = Decimal(elem.text.replace(',', '.'))
        if (action == 'end' and elem.tag == 'product_id'):
            product_id = int(elem.text)
        if (action == 'end' and elem.tag == 'shop_url'):
            shop_url = str(elem.text)

    logging.debug(products)
    if (len(products) == 0):
        return (None, None)
    return products.popitem()[1]


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
        (price, url) = get_price_and_url_from_nokaut(product_name=product,
                                                     nokaut_key=key)
        print(price, url)


if __name__ == "__main__":
    main()
