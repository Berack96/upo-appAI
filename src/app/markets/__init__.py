from src.app.markets.base import BaseWrapper
from src.app.markets.coinbase import CoinBaseWrapper
from src.app.markets.cryptocompare import CryptoCompareWrapper

from agno.utils.log import log_warning

class MarketAPIs(BaseWrapper):
    """
    Classe per gestire le API di mercato disponibili.
    Permette di ottenere un'istanza della prima API disponibile in base alla priorità specificata.
    """

    @staticmethod
    def get_list_available_market_apis(currency: str = "USD") -> list[BaseWrapper]:
        """
        Restituisce una lista di istanze delle API di mercato disponibili.
        La priorità è data dall'ordine delle API nella lista wrappers.
        1. CoinBase
        2. CryptoCompare

        :param currency: Valuta di riferimento (default "USD")
        :return: Lista di istanze delle API di mercato disponibili
        """
        wrapper_builders = [
            CoinBaseWrapper,
            CryptoCompareWrapper,
        ]

        result = []
        for wrapper in wrapper_builders:
            try:
                result.append(wrapper(currency=currency))
            except Exception as e:
                log_warning(f"{wrapper} cannot be initialized: {e}")

        assert result, "No market API keys set in environment variables."
        return result

    def __init__(self, currency: str = "USD"):
        """
        Inizializza la classe con la valuta di riferimento e la priorità dei provider.

        Args:
            currency: Valuta di riferimento (default "USD")
        """
        self.currency = currency
        self.wrappers = MarketAPIs.get_list_available_market_apis(currency=currency)

    # Metodi che semplicemente chiamano il metodo corrispondente del primo wrapper disponibile
    # TODO magari fare in modo che se il primo fallisce, prova con il secondo, ecc.
    # oppure fare un round-robin tra i vari wrapper oppure usarli tutti e fare una media dei risultati
    def get_product(self, asset_id):
        return self.wrappers[0].get_product(asset_id)
    def get_products(self, asset_ids: list):
        return self.wrappers[0].get_products(asset_ids)
    def get_all_products(self):
        return self.wrappers[0].get_all_products()
    def get_historical_prices(self, asset_id = "BTC"):
        return self.wrappers[0].get_historical_prices(asset_id)
