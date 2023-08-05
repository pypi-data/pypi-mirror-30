from cryptojp import bitflyer
from cryptojp import coincheck
from cryptojp import btcbox
from cryptojp import kraken
from cryptojp import quoine


def NewExchange(exchange_name, apikey, secretkey):
    if exchange_name == "bitflyer":
        return bitflyer.Bitflyer(apikey, secretkey)
    elif exchange_name == "coincheck":
        return coincheck.Coincheck(apikey, secretkey)
    elif exchange_name == "btcbox":
        return btcbox.Btcbox(apikey, secretkey)
    elif exchange_name == "kraken":
        return kraken.Kraken(apikey, secretkey)
    elif exchange_name == "quoine":
        return quoine.Quoine(apikey, secretkey)
    raise ValueError("error!")
