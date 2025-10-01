from typing import List, Optional
from agno.tools import Toolkit
from app.utils.wrapper_handler import WrapperHandler
from .base import BaseWrapper, ProductInfo, Price
from .coinbase import CoinBaseWrapper
from .binance import BinanceWrapper
from .cryptocompare import CryptoCompareWrapper
from .yfinance import YFinanceWrapper
from .binance_public import PublicBinanceAgent

__all__ = [ "MarketAPIs", "BinanceWrapper", "CoinBaseWrapper", "CryptoCompareWrapper", "YFinanceWrapper", "PublicBinanceAgent" ]


class MarketAPIsTool(BaseWrapper, Toolkit):
    """
    Classe per gestire le API di mercato disponibili.

    Supporta due modalità:
    1. **Modalità standard** (default): usa il primo wrapper disponibile
    2. **Modalità aggregazione**: aggrega dati da tutte le fonti disponibili

    L'aggregazione può essere abilitata/disabilitata dinamicamente.
    """

    def __init__(self, currency: str = "USD", enable_aggregation: bool = False):
        self.currency = currency
        wrappers = [ BinanceWrapper, CoinBaseWrapper, CryptoCompareWrapper, YFinanceWrapper ]
        self.wrappers: WrapperHandler[BaseWrapper] = WrapperHandler.build_wrappers(wrappers)

        # Inizializza l'aggregatore solo se richiesto (lazy initialization)
        self._aggregator = None
        self._aggregation_enabled = enable_aggregation

        Toolkit.__init__(
            self,
            name="Market APIs Toolkit",
            tools=[
                self.get_product,
                self.get_products,
                self.get_all_products,
                self.get_historical_prices,
            ],
        )

    def _get_aggregator(self):
        """Lazy initialization dell'aggregatore"""
        if self._aggregator is None:
            from app.utils.market_data_aggregator import MarketDataAggregator
            self._aggregator = MarketDataAggregator(self.currency)
            self._aggregator.enable_aggregation(self._aggregation_enabled)
        return self._aggregator

    def get_product(self, asset_id: str) -> Optional[ProductInfo]:
        """Ottieni informazioni su un prodotto specifico"""
        if self._aggregation_enabled:
            return self._get_aggregator().get_product(asset_id)
        return self.wrappers.try_call(lambda w: w.get_product(asset_id))

    def get_products(self, asset_ids: List[str]) -> List[ProductInfo]:
        """Ottieni informazioni su multiple prodotti"""
        if self._aggregation_enabled:
            return self._get_aggregator().get_products(asset_ids)
        return self.wrappers.try_call(lambda w: w.get_products(asset_ids))

    def get_all_products(self) -> List[ProductInfo]:
        """Ottieni tutti i prodotti disponibili"""
        if self._aggregation_enabled:
            return self._get_aggregator().get_all_products()
        return self.wrappers.try_call(lambda w: w.get_all_products())

    def get_historical_prices(self, asset_id: str = "BTC", limit: int = 100) -> List[Price]:
        """Ottieni dati storici dei prezzi"""
        if self._aggregation_enabled:
            return self._get_aggregator().get_historical_prices(asset_id, limit)
        return self.wrappers.try_call(lambda w: w.get_historical_prices(asset_id, limit))

    # Metodi per controllare l'aggregazione
    def enable_aggregation(self, enabled: bool = True):
        """Abilita/disabilita la modalità aggregazione"""
        self._aggregation_enabled = enabled
        if self._aggregator:
            self._aggregator.enable_aggregation(enabled)

    def is_aggregation_enabled(self) -> bool:
        """Verifica se l'aggregazione è abilitata"""
        return self._aggregation_enabled

    # Metodo speciale per debugging (opzionale)
    def get_aggregated_product_with_debug(self, asset_id: str) -> dict:
        """
        Metodo speciale per ottenere dati aggregati con informazioni di debug.
        Disponibile solo quando l'aggregazione è abilitata.
        """
        if not self._aggregation_enabled:
            raise RuntimeError("L'aggregazione deve essere abilitata per usare questo metodo")
        return self._get_aggregator().get_aggregated_product_with_debug(asset_id)

# TODO definire istruzioni per gli agenti di mercato
MARKET_INSTRUCTIONS = """

"""