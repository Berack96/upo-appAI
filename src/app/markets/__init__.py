from agno.tools import Toolkit
from app.markets.base import BaseWrapper, Price, ProductInfo
from app.markets.binance import BinanceWrapper
from app.markets.coinbase import CoinBaseWrapper
from app.markets.cryptocompare import CryptoCompareWrapper
from app.markets.yfinance import YFinanceWrapper
from app.utils.market_aggregation import aggregate_history_prices, aggregate_product_info
from app.utils.wrapper_handler import WrapperHandler

__all__ = [ "MarketAPIsTool", "BinanceWrapper", "CoinBaseWrapper", "CryptoCompareWrapper", "YFinanceWrapper", "ProductInfo", "Price" ]


class MarketAPIsTool(BaseWrapper, Toolkit):
    """
    Class that aggregates multiple market API wrappers and manages them using WrapperHandler.
    This class supports retrieving product information and historical prices.
    This class can also aggregate data from multiple sources to provide a more comprehensive view of the market.
    The following wrappers are included in this order:
    - BinanceWrapper
    - YFinanceWrapper
    - CoinBaseWrapper
    - CryptoCompareWrapper
    """

    def __init__(self, currency: str = "USD"):
        """
        Initialize the MarketAPIsTool with multiple market API wrappers.
        The following wrappers are included in this order:
        - BinanceWrapper
        - YFinanceWrapper
        - CoinBaseWrapper
        - CryptoCompareWrapper
        Args:
            currency (str): Valuta in cui restituire i prezzi. Default è "USD".
        """
        kwargs = {"currency": currency or "USD"}
        wrappers = [ BinanceWrapper, YFinanceWrapper, CoinBaseWrapper, CryptoCompareWrapper ]
        self.wrappers: WrapperHandler[BaseWrapper] = WrapperHandler.build_wrappers(wrappers, kwargs=kwargs)

        Toolkit.__init__(
            self,
            name="Market APIs Toolkit",
            tools=[
                self.get_product,
                self.get_products,
                self.get_historical_prices,
                self.get_products_aggregated,
                self.get_historical_prices_aggregated,
            ],
        )

    def get_product(self, asset_id: str) -> ProductInfo:
        return self.wrappers.try_call(lambda w: w.get_product(asset_id))
    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        return self.wrappers.try_call(lambda w: w.get_products(asset_ids))
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
        Raises:
            Exception: If all wrappers fail to provide results.
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
        Raises:
            Exception: If all wrappers fail to provide results.
        """
        all_prices = self.wrappers.try_call_all(lambda w: w.get_historical_prices(asset_id, limit))
        return aggregate_history_prices(all_prices)
