import urllib2
import urllib
from lxml import etree


def get_proce_and_url_from_nokaut(product_name='', nokaut_key=''):
    method = 'nokaut.Price.getByProductName'
    method_param = 'name'

    url_params = {'format': 'xml', 'key': nokaut_key, 'method': method,
                  method_param: product_name, 'sortDirection': 'price'}
    url_params = urllib.urlencode(url_params)

    nokaut_url = 'http://api.nokaut.pl/?%s' % url_params
    print nokaut_url
    response = urllib2.urlopen(nokaut_url)
    xml = response.read()

    print xml
    indent = ''

    root = etree.XML(xml)
    context = etree.iterwalk(root, events=("start", "end"),
                             tag=('item', 'price', 'product_id', 'shop_url'))

    products = dict()
    price = 0.0
    shop_url = ''
    product_id = 0

    for action, elem in context:
        if(action == 'end' and elem.tag == 'item'):
            (old_price, old_shop_url) = products.setdefault(product_id, (price, shop_url))
            if(price < old_price):
                products[product_id] = (price, shop_url)
        if(action == 'end' and elem.tag == 'price'):
            price = float(elem.text.replace(',', '.'))
        if(action == 'end' and elem.tag == 'product_id'):
            product_id = int(elem.text)
        if(action == 'end' and elem.tag == 'shop_url'):
            shop_url = str(elem.text)

        if(action == 'start'):
            indent += '    '
        if(action == 'end'):
            print("    %s %s %s" % (indent, elem.tag, elem.text))
            indent = indent[0:-4]

    print products
    if(len(products) == 0):
        return (None, None)
    return products.popitem()[1]
