import urllib2
import urllib
from lxml import etree
import sys
import getopt


def get_proce_and_url_from_nokaut(product_name='', nokaut_key=''):
    method = 'nokaut.Price.getByProductName'
    method_param = 'name'

    url_params = {'format': 'xml', 'key': nokaut_key, 'method': method,
                  method_param: product_name, 'sortDirection': 'price'}
    url_params = urllib.urlencode(url_params)

    nokaut_url = 'http://api.nokaut.pl/?%s' % url_params
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


def usage():
    print("nokaut -p 'product_name' -k 'your_nokaut_key'")


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:k:", ["help", "product=", "key="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    key = None
    product = None

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(1)
        elif o in ("-p", "--product"):
            product = a
        elif o in ("-k", "--key"):
            key = a
        else:
            usage()
            sys.exit(2)

    if(key is None or product is None):
        usage()
        sys.exit(2)
    else:
        (price, url) = get_proce_and_url_from_nokaut(product_name=product,
                                                     nokaut_key=key)
        print(price, url)  

if __name__ == "__main__":
    main()
