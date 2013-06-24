from decimal import Decimal
import mechanize
import urllib
import logging
from BeautifulSoup import BeautifulSoup

logging.basicConfig(filename='pythonpath.log', level=logging.DEBUG)


def get_price_and_url_from_allegro(product_name=''):
    """This function finds a offer of product with the lowest price in the
    allegro.pl portal. It returns a tuple with lowest price and a url to
    the offer in allegro.pl.

    :param product_name: The name of product to search for in nokaut.pl.
    :type product_name: str.
    :returns: (Decimal,str) -- the lowest price of product and url to the shop.

    """

    product_name_encoded = urllib.urlencode({'string': product_name})
    search_address = \
        'http://allegro.pl/listing/listing.php?%s&description=1&order=p' \
        % product_name_encoded

    response = mechanize.urlopen(search_address)
    forms = mechanize.ParseResponse(response, backwards_compat=False)
    logging.debug(response.geturl())
    response.close()
    html = ''

    for form in forms:
        for control in form.controls:
            if (control.name == 'offerTypeBuyNow'):
                control.items[0].selected = True
            elif (control.name == 'standard_allegro'):
                control.items[0].selected = True
            elif (control.name == 'string'):
                pass
            elif (control.name == 'description'):
                pass
            elif (control.name == 'order'):
                pass
            else :
                control.disabled = True

        if (form.name == 'display-form'):
            request1 = form.click()
            try:
                logging.debug(request1)
                response1 = mechanize.urlopen(request1)
                html = response1.read()
            except mechanize.HTTPError, response1:
                pass

    url = ''
    price = Decimal(0.0)
    soup = BeautifulSoup(html)
    sections = soup.findAll('section', {'class': 'offers'})
    for section in sections:
        h2tag = section.find('h2', {'class': 'listing-header'})
        if (h2tag.string == 'lista ofert'):
            header = section.find('header')
            url = header.find('a', href=True)['href']
            if (url != ''):
                url = 'www.allegro.pl%s' % url
            url = str(url)
            price = section.find('span', {'class': 'buy-now dist'}).contents[2]
            price = price.replace(' ', '').replace(',', '.')
            price = Decimal(price)

    logging.debug((price, url))
    return (price, url)
