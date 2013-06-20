import urllib2
import urllib
from lxml import etree

def nokaut(product_name='canon450d',
           nokaut_key='a8839b1180ea00fa1cf7c6b74ca01bb5'):
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
    context = etree.iterwalk(root, events=("start", "end"), tag=('price',))

    for action, elem in context:
        if(action == 'start'):
            indent += '    '
            print("%s%s %s" % (indent, action, elem.tag))
        if(action == 'end'):
            print("    %s %s" % (indent, elem.text))
            print("%s%s %s" % (indent, action, elem.tag))
            indent = indent[0:-4]
    return xml