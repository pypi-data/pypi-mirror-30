# -*- coding: utf-8 -*-

"""
trading212api._internal_utils
~~~~~~~~~~~~~~

This module provides utils used local.
"""

_base = "https://www.trading212.com/"
_base_mode = "https://%s.trading212.com/"
_base_rest = _base_mode + "rest/v2/"

URLS = {
    'auth': _base + "en/authenticate",
    'login': _base_mode + "login",  # replacement with mode
    'account': _base_rest + "account",
    'open-pos': _base_rest + "trading/open-positions",
    'close-pos': _base_rest + "trading/open-positions/close/%s",
    'instrum-update': _base_rest + "prices?instrumentCodes=%s&withFakes=true",
    'max-quant': _base_rest + "max-quantities?instrumentCodes=%s",
    'candles': "https://%s.trading212.com/charting/rest/v2/candles",
    'margin': _base_rest + "tradingAdditionalInfo?instrumentCode=%s&positionId=null&quantity=%d",
}

ENCOD = {
    ',': "%2C"
}

PARAMS = {
    'username': 'login[username]',
    'password': 'login[password]',
    'client': 'X-Trader-Client',
    # for laziness
    'instr': "instrumentCode",
    'trgprc': "targetPrice",
    'cont': "Content-Type",
    'json': "application/json",
}

INSTRUMS = ['EURUSD', 'EURUSD_ZERO', 'GBPUSD', 'GBPUSD_ZERO', 'USDCAD', 'USDCAD_ZERO', 'USDCHF',
            'USDCHF_ZERO', 'USDJPY', 'USDJPY_ZERO']
