#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from .base.exchange import *
from .errors import *
import sys
if sys.version_info.major <= 2:
    from urllib import urlencode
else:
    from urllib.parse import urlencode
import requests
import hmac
import hashlib
import json
BITFLYER_REST_URL = 'api.bitflyer.jp'


class Bitflyer(Exchange):
    def __init__(self, apikey, secretkey):
        def httpGet(url, resource, params, apikey, secretkey):
            timestamp = str(time.time())
            text = str.encode(timestamp + "GET" + resource + urlencode(params))
            headers = {
                "ACCESS-KEY": apikey,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-SIGN": hmac.new(str.encode(secretkey), text, hashlib.sha256).hexdigest(),
                'Content-Type': 'application/json',
            }
            return self.session.get('https://' + url + resource,
                                    headers=headers, data=params).json()

        def httpPost(url, resource, params, apikey, secretkey):
            timestamp = str(time.time())
            text = str.encode(timestamp + "POST" +
                              resource + json.dumps(params))
            headers = {
                "ACCESS-KEY": apikey,
                "ACCESS-TIMESTAMP": timestamp,
                "ACCESS-SIGN": hmac.new(str.encode(secretkey), text, hashlib.sha256).hexdigest(),
                'Content-Type': 'application/json',
            }
            return self.session.post('https://' + url + resource,
                                     headers=headers, data=json.dumps(params)).json()
        super(Bitflyer, self).__init__(apikey, secretkey)
        self.session = requests.session()
        self.httpPost = httpPost
        self.httpGet = httpGet

    def __del__(self):
        self.session.close()

    def markets(self):
        MARKETS_RESOURCE = "/v1/markets"
        json = self.session.get('https://' + BITFLYER_REST_URL +
                                MARKETS_RESOURCE).json()
        product_codes = [j["product_code"].split("_") for j in json if len(j["product_code"].split("_")) == 2]
        return tuple([CurrencyPair(trading=p[0].upper(), settlement=p[1].upper()) for p in product_codes])

    def settlements(self):
        MARKETS_RESOURCE = "/v1/markets"
        json = self.session.get('https://' + BITFLYER_REST_URL +
                                MARKETS_RESOURCE).json()
        settlements = [j["product_code"].split("_")[1] for j in json if len(j["product_code"].split("_")) == 2]
        return tuple(set(settlements))

    def ticker(self, trading, settlement):
        TICKER_RESOURCE = "/v1/ticker"
        params = {}
        params["product_code"] = trading + "_" + settlement
        json = self.session.get('https://' + BITFLYER_REST_URL +
                                TICKER_RESOURCE, data=params).json()
        return Ticker(
            timestamp=json["timestamp"],
            last=float(json["ltp"]),
            high=None,
            low=None,
            bid=float(json["best_bid"]),
            ask=float(json["best_ask"]),
            volume=float(json["volume"])
        )

    def board(self, item=''):
        BOARD_RESOURCE = "/v1/board"
        params = {}
        json = self.session.get('https://' + BITFLYER_REST_URL +
                                BOARD_RESOURCE, data=params).json()
        return Board(
            asks=[Ask(price=float(ask["price"]), size=float(ask["size"]))
                  for ask in json["asks"]],
            bids=[Bid(price=float(bid["price"]), size=float(bid["size"]))
                  for bid in json["bids"]],
            mid_price=float(json["mid_price"])
        )

    def order(self, trading, settlement, order_type, side, price, size):
        ORDER_RESOURCE = "/v1/me/sendchildorder"
        params = {
            "product_code": trading + "_" + settlement,
            "child_order_type": order_type.upper(),
            "side": side.upper(),
            "price": price,
            "size": size
        }
        if order_type.lower() != "limit":
            params.pop('price')

        json = self.httpPost(BITFLYER_REST_URL,
                             ORDER_RESOURCE, params, self._apikey, self._secretkey)
        return json["child_order_acceptance_id"]

    def get_open_orders(self, symbol="BTC_JPY"):
        OPEN_ORDERS_RESOURCE = "/v1/me/getchildorders"
        params = {"child_order_state": "ACTIVE"}
        if symbol:
            params["product_code"] = symbol
        json = self.httpGet(BITFLYER_REST_URL,
                            OPEN_ORDERS_RESOURCE, params, self._apikey, self._secretkey)
        return json

    def cancel_order(self, symbol, order_id):
        CANCEL_ORDERS_RESOURCE = "/v1/me/cancelchildorder"
        params = {
            "product_code": symbol,
            "child_order_acceptance_id": order_id,
        }
        self.httpPost(BITFLYER_REST_URL,
                      CANCEL_ORDERS_RESOURCE, params, self._apikey, self._secretkey)

    def get_fee(self, symbol="BTC_JPY"):
        GET_FEE_RESOURCE = "/v1/me/gettradingcommission"
        params = {
            "product_code": symbol,
        }
        json = self.httpGet(BITFLYER_REST_URL, GET_FEE_RESOURCE, params, self._apikey, self._secretkey)
        return json["commission_rate"]

    def balance(self):
        BALANCE_RESOURCE = "/v1/me/getbalance"
        params = {
        }
        json = self.httpGet(BITFLYER_REST_URL,
                            BALANCE_RESOURCE, params, self._apikey, self._secretkey)
        balances = {}
        for j in json:
            balances[j['currency_code']] = [j["amount"], j["available"]]
        return balances
