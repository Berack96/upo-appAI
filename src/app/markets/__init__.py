import os
from app.markets.base import BaseWrapper
from app.markets.coinbase import CoinBaseWrapper
from app.markets.cryptocompare import CryptoCompareWrapper

# TODO Dare la priorità in base alla qualità del servizio
# TODO Aggiungere altri wrapper se necessario
def get_first_available_market_api(currency:str = "USD") -> BaseWrapper:
    """
    Restituisce il primo wrapper disponibile in base alle configurazioni del file .env e alle chiavi API presenti.
    La priorità è data a Coinbase, poi a CryptoCompare.
    Se non sono presenti chiavi API, restituisce una eccezione.
    :param currency: Valuta di riferimento (default "USD")
    :return: Lista di istanze di wrapper
    """
    return get_list_available_market_apis(currency=currency)[0]

def get_list_available_market_apis(currency:str = "USD") -> list[BaseWrapper]:
    """
    Restituisce la lista di wrapper disponibili in base alle configurazioni del file .env e alle chiavi API presenti.
    La priorità è data a Coinbase, poi a CryptoCompare.
    Se non sono presenti chiavi API, restituisce una eccezione.
    :param currency: Valuta di riferimento (default "USD")
    :return: Lista di istanze di wrapper
    """
    wrappers = []

    api_key = os.getenv("COINBASE_API_KEY")
    api_secret = os.getenv("COINBASE_API_SECRET")
    if api_key and api_secret:
        wrappers.append(CoinBaseWrapper(api_key=api_key, api_private_key=api_secret, currency=currency))

    api_key = os.getenv("CRYPTOCOMPARE_API_KEY")
    if api_key:
        wrappers.append(CryptoCompareWrapper(api_key=api_key, currency=currency))

    assert wrappers, "No valid API keys set in environment variables."
    return wrappers
