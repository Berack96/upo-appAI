from agno.tools import Toolkit
from app.utils.wrapper_handler import WrapperHandler
from app.utils.market_aggregation import aggregate_product_info, aggregate_history_prices
from .base import BaseWrapper, ProductInfo, Price
from .coinbase import CoinBaseWrapper
from .binance import BinanceWrapper
from .cryptocompare import CryptoCompareWrapper
from .yfinance import YFinanceWrapper

__all__ = [ "MarketAPIs", "BinanceWrapper", "CoinBaseWrapper", "CryptoCompareWrapper", "YFinanceWrapper" ]


class MarketAPIsTool(BaseWrapper, Toolkit):
    """
    Classe per comporre più MarketAPI con gestione degli errori e aggregazione dei dati.
    Usa WrapperHandler per gestire più API con logica di retry e failover.
    Si può scegliere se aggregare i dati da tutte le fonti o usare una singola fonte tramite delle chiamate apposta.
    """

    def __init__(self, currency: str = "USD"):
        kwargs = {"currency": currency or "USD"}
        wrappers = [ BinanceWrapper, CoinBaseWrapper, CryptoCompareWrapper, YFinanceWrapper ]
        self.wrappers: WrapperHandler[BaseWrapper] = WrapperHandler.build_wrappers(wrappers, kwargs=kwargs)

        Toolkit.__init__(
            self,
            name="Market APIs Toolkit",
            tools=[
                self.get_product,
                self.get_products,
                self.get_all_products,
                self.get_historical_prices,
                self.get_products_aggregated,
                self.get_historical_prices_aggregated,
            ],
        )

    def get_product(self, asset_id: str) -> ProductInfo:
        return self.wrappers.try_call(lambda w: w.get_product(asset_id))
    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        return self.wrappers.try_call(lambda w: w.get_products(asset_ids))
    def get_all_products(self) -> list[ProductInfo]:
        return self.wrappers.try_call(lambda w: w.get_all_products())
    def get_historical_prices(self, asset_id: str = "BTC", limit: int = 100) -> list[Price]:
        return self.wrappers.try_call(lambda w: w.get_historical_prices(asset_id, limit))


    def get_products_aggregated(self, asset_ids: list[str]) -> list[ProductInfo]:
        """
        Restituisce i dati aggregati per una lista di asset_id.\n
        Attenzione che si usano tutte le fonti, quindi potrebbe usare molte chiamate API (che potrebbero essere a pagamento).
        Args:
            asset_ids (list[str]): Lista di asset_id da cercare.
        Returns:
            list[ProductInfo]: Lista di ProductInfo aggregati.
        """
        all_products = self.wrappers.try_call_all(lambda w: w.get_products(asset_ids))
        return aggregate_product_info(all_products)

    def get_historical_prices_aggregated(self, asset_id: str = "BTC", limit: int = 100) -> list[Price]:
        """
        Restituisce i dati storici aggregati per un asset_id. Usa i dati di tutte le fonti disponibili e li aggrega.\n
        Attenzione che si usano tutte le fonti, quindi potrebbe usare molte chiamate API (che potrebbero essere a pagamento).
        Args:
            asset_id (str): Asset ID da cercare.
            limit (int): Numero massimo di dati storici da restituire.
        Returns:
            list[Price]: Lista di Price aggregati.
        """
        all_prices = self.wrappers.try_call_all(lambda w: w.get_historical_prices(asset_id, limit))
        return aggregate_history_prices(all_prices)

# TODO definire istruzioni per gli agenti di mercato
MARKET_INSTRUCTIONS = """

"""