# -*- coding: utf-8 -*-

"""
trading212api.exceptions
~~~~~~~~~~~~~~

This module contains all exceptions.
"""


class RequestError(Exception):
    """raised when status_code different from 200"""

    def __init__(self, response):
        self.status = response.status_code
        if self.status == 500:  # internal error
            details = response.json()['context']
            if details['type'] == 'PriceChangedException':  # if price has changed
                raise PriceChangedException(details['current'])
            elif details['type'] == 'MinQuantityExceeded':  # if min not respected
                raise MinQuantityExceeded(details['min'])
            elif details['type'] in ['MaxBuyQuantityExceeded', 'MaxSellQuantityExceeded']:
                if details['max'] == 0:
                    raise ProductNotAvaible()
                else:
                    raise MaxQuantityExceeded(details['max'])
            elif details['type'] == 'NoPriceException':
                raise NoPriceException()
            elif details['type'] == 'MarketStillNotOpen':
                raise MarketClosed()
            else:
                super().__init__("500 - Response:%s" % response.json())
                return
        super().__init__("Request error %d" % response.status_code)


class InvalidCredentials(Exception):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        super().__init__("Invalid credentials for %s" % username)


class PriceChangedException(Exception):
    def __init__(self, price):
        self.price = price
        super().__init__("Price changed to %f" % price)


class MinQuantityExceeded(Exception):
    def __init__(self, mn):
        self.limit = mn
        super().__init__("Below min quantity of %d" % mn)


class MaxQuantityExceeded(Exception):
    def __init__(self, mx):
        self.limit = mx
        super().__init__("Above max quantity of %d" % mx)


class ProductNotAvaible(Exception):
    def __init__(self):
        super().__init__("Product is not avaible")


class NoPriceException(Exception):
    def __init__(self):
        super().__init__("NoPriceException caught")


class LiveNotConfigured(Exception):
    def __init__(self):
        super().__init__("Live mode not configured")


class MarketClosed(Exception):
    def __init__(self):
        super().__init__("Market closed for this instrument")