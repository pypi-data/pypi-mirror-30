#!/usr/bin/python
# -*- coding: utf-8 -*-
from .base.exchange import *
import requests

HITBTC_REST_URL = 'api.hitbtc.com'


class Hitbtc(Exchange):
    def __init__(self, apikey, secretkey):
        super(Hitbtc, self).__init__(apikey, secretkey)
        self.session = requests.session()
        self.session.auth = (self._apikey, self._secretkey)

    def __del__(self):
        self.session.close()

    def markets(self):
        MARKETS_RESOURCE = "/api/2/public/symbol"
        json = self.session.get('https://' + HITBTC_REST_URL +
                                MARKETS_RESOURCE).json()
        return list([CurrencyPair(trading=j["baseCurrency"], settlement=j["quoteCurrency"]) for j in json])

    def settlements(self):
        SETTLEMENTS_RESOURCE = "/api/2/public/symbol"
        json = self.session.get('https://' + HITBTC_REST_URL +
                                SETTLEMENTS_RESOURCE).json()
        return list(set([j["quoteCurrency"] for j in json]))

    def ticker(self, item='BTCUSD'):
        TICKER_RESOURCE = "/api/2/public/ticker/" + item
        json = self.session.get('https://' + HITBTC_REST_URL +
                                TICKER_RESOURCE).json()
        return Ticker(
            timestamp=json["timestamp"],
            last=float(json["last"]),
            high=float(json["high"]),
            low=float(json["low"]),
            bid=float(json["bid"]),
            ask=float(json["ask"]),
            volume=float(json["volume"])
        )

    def board(self, item='BTCUSD'):
        BOARD_RESOURCE = "/api/2/public/orderbook/" + item
        json = self.session.get('https://' + HITBTC_REST_URL +
                                BOARD_RESOURCE).json()
        return Board(
            asks=[Ask(price=float(ask["price"]), size=float(ask["size"]))
                  for ask in json["ask"]],
            bids=[Bid(price=float(bid["price"]), size=float(bid["size"]))
                  for bid in json["bid"]],
            mid_price=(float(json["ask"][0]["price"]) + float(json["bid"][0]["price"])) / 2)

    def order(self, trading, settlement, order_type, side, price, size):
        ORDER_RESOURCE = "/api/2/order"

        params = {
            "symbol": trading.lower() + settlement.lower(),
            "side": side.lower(),
            "quantity": size,
            "price": price
        }
        if order_type != "" and order_type.lower() != "limit":
            params['type'] = order_type.lower()
            params.pop('price')
        json = self.session.post('https://' + HITBTC_REST_URL +
                                 ORDER_RESOURCE, data=params).json()
        return json["clientOrderId"]

    def get_open_orders(self, symbol="BTCUSD"):
        OPEN_ORDERS_RESOURCE = "/api/2/order"
        params = {"symbol": symbol}
        json = self.session.get('https://' + HITBTC_REST_URL +
                                OPEN_ORDERS_RESOURCE).json()
        return json

    def cancel_order(self, symbol,order_id):
        CANCEL_ORDER_RESOURCE = "/api/2/order/"+order_id
        self.session.delete('https://' + HITBTC_REST_URL +
                            CANCEL_ORDER_RESOURCE).json()

    def get_fee(self, symbol = "BTCUSD"):
        GET_FEE_RESOURCE = "/api/2/trading/fee/"+symbol
        json = self.session.get('https://' + HITBTC_REST_URL +
                            GET_FEE_RESOURCE).json()
        return [json["takeLiquidityRate"], json['provideLiquidityRate']]

    def balance(self):
        BALANCE_RESOURCE = "/api/2/trading/balance"

        session = requests.session()
        session.auth = (self._apikey, self._secretkey)
        json = self.session.get('https://' + HITBTC_REST_URL +
                                BALANCE_RESOURCE).json()

        balances = {}
        for j in json:
            al = float(j["available"]) + float(j["reserved"])
            balances[j['currency']] = [al, float(j["available"])]
        return balances
