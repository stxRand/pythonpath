import urllib
import logging
from decimal import Decimal

import sys
import os
sys.path.insert(0, 'libs')
sys.path.insert(0, os.path.join('pythonpath','libs'))
import mechanize
from bs4 import BeautifulSoup

from offer_provider import OfferProvider


logging.basicConfig(filename='pythonpath.log', level=logging.DEBUG)


class Allegro(OfferProvider):
    """The class allow to search for a product in the allegro.pl
    with the lowest price"""

    def __init__(self, product_name=''):
        self.product_name = product_name
        self._price = Decimal(0.0)
        self._url = ''

    def search(self, product_name=None):
        """Finds a offer of product with the lowest price in the
        allegro.pl portal. It returns a tuple with lowest price and a url to
        the offer in allegro.pl.

        :param product_name: The name of product to search for in allegro.pl.
        :type product_name: str.
        :returns: (Decimal,str) -- the lowest price of product and url to the shop.

        """

        if (product_name is not None):
            self.product_name = product_name

        search_address = self.__prepare_initial_allegro_url(self.product_name)
        forms = self.__get_forms_with_mechanize(search_address)
        html = self.__prepare_and_send_advanced_search_form(forms)
        (self._price, self._url) = self.__find_price_and_url_in_html(html)

        logging.debug((self._price, self._url))
        return (self._price, self._url)

    def get_lowest_price(self):
        """Returns the lowest price from the last search"""

        return self._price

    def get_offer_url(self):
        """Returns a offer url from the last search"""

        return self._url

    def __prepare_initial_allegro_url(self, product_name):
        product_name_encoded = urllib.urlencode({'string': product_name})
        search_address = \
            'http://allegro.pl/listing/listing.php?%s&description=1&order=p' \
            % product_name_encoded
        return search_address

    def __get_forms_with_mechanize(self, search_address):
        response = mechanize.urlopen(search_address)
        forms = mechanize.ParseResponse(response, backwards_compat=False)
        logging.debug(response.geturl())
        response.close()
        return forms

    def __send_advanced_search_form(self, form):
        html = ''
        request1 = form.click()
        try:
            logging.debug(request1)
            response1 = mechanize.urlopen(request1)
            html = response1.read()
        except mechanize.HTTPError, response1:
            pass
        return html

    def __prepare_and_send_advanced_search_form(self, forms):
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
                else:
                    control.disabled = True

            if (form.name == 'display-form'):
                html = self.__send_advanced_search_form(form)
        return html

    def __parse_url(self, section):
        header = section.find('header')
        url = header.find('a', href=True)['href']
        if (url != ''):
            url = 'http://www.allegro.pl%s' % url
        return str(url)

    def __parse_price(self, section):
        price = section.find('span', {'class': 'buy-now dist'}).contents[2]
        price = price.replace(' ', '').replace(',', '.')
        return Decimal(price)

    def __find_price_and_url_in_html(self, html):
        url = ''
        price = Decimal(0.0)

        soup = BeautifulSoup(html)
        section_tags = soup.findAll('section', {'class': 'offers'})

        for section_tag in section_tags:
            h2tag = section_tag.find('h2', {'class': 'listing-header'})
            if (h2tag.string == 'lista ofert'):
                url = self.__parse_url(section_tag)
                price = self.__parse_price(section_tag)

        return (price, url)
