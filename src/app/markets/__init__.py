from .base import BaseWrapper
from .coinbase import CoinBaseWrapper
from .cryptocompare import CryptoCompareWrapper
from .binance import BinanceWrapper
from .binance_public import PublicBinanceAgent
from .error_handler import ProviderFallback, MarketAPIError, safe_execute

from agno.utils.log import log_warning
import logging

logger = logging.getLogger(__name__)

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
        self.fallback_manager = ProviderFallback(self.wrappers)

    # Metodi con fallback robusto tra provider multipli
    def get_product(self, asset_id: str):
        """Ottiene informazioni su un prodotto con fallback automatico tra provider."""
        try:
            return self.fallback_manager.execute_with_fallback("get_product", asset_id)
        except MarketAPIError as e:
            logger.error(f"Failed to get product {asset_id}: {str(e)}")
            raise

    def get_products(self, asset_ids: list):
        """Ottiene informazioni su più prodotti con fallback automatico tra provider."""
        try:
            return self.fallback_manager.execute_with_fallback("get_products", asset_ids)
        except MarketAPIError as e:
            logger.error(f"Failed to get products {asset_ids}: {str(e)}")
            raise

    def get_all_products(self):
        """Ottiene tutti i prodotti con fallback automatico tra provider."""
        try:
            return self.fallback_manager.execute_with_fallback("get_all_products")
        except MarketAPIError as e:
            logger.error(f"Failed to get all products: {str(e)}")
            raise

    def get_historical_prices(self, asset_id: str = "BTC"):
        """Ottiene prezzi storici con fallback automatico tra provider."""
        try:
            return self.fallback_manager.execute_with_fallback("get_historical_prices", asset_id)
        except MarketAPIError as e:
            logger.error(f"Failed to get historical prices for {asset_id}: {str(e)}")
            raise
