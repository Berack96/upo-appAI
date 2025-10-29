from agno.tools import Toolkit
from app.api.wrapper_handler import WrapperHandler
from app.api.core.markets import MarketWrapper, Price, ProductInfo
from app.api.markets import BinanceWrapper, CoinBaseWrapper, CryptoCompareWrapper, YFinanceWrapper

class MarketAPIsTool(MarketWrapper, Toolkit):
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
        wrappers: list[type[MarketWrapper]] = [BinanceWrapper, YFinanceWrapper, CoinBaseWrapper, CryptoCompareWrapper]
        self.handler = WrapperHandler.build_wrappers(wrappers, kwargs=kwargs)

        Toolkit.__init__( # type: ignore
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
        """
        Gets product information for a *single* asset from the *first available* provider.

        This method sequentially queries multiple market data sources and returns
        data from the first one that responds successfully.
        Use this for a fast, specific lookup of one asset.

        Args:
            asset_id (str): The ID of the asset to retrieve information for.

        Returns:
            ProductInfo: An object containing the product information.
        """
        return self.handler.try_call(lambda w: w.get_product(asset_id))

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        """
        Gets product information for a *list* of assets from the *first available* provider.

        This method sequentially queries multiple market data sources and returns
        data from the first one that responds successfully.
        Use this for a fast lookup of multiple assets.

        Args:
            asset_ids (list[str]): The list of asset IDs to retrieve information for.

        Returns:
            list[ProductInfo]: A list of objects containing product information.
        """
        return self.handler.try_call(lambda w: w.get_products(asset_ids))

    def get_historical_prices(self, asset_id: str, limit: int = 100) -> list[Price]:
        """
        Gets historical price data for a *single* asset from the *first available* provider.

        This method sequentially queries multiple market data sources and returns
        data from the first one that responds successfully.
        Use this for a fast lookup of price history.

        Args:
            asset_id (str): The asset ID to retrieve price data for.
            limit (int): The maximum number of price data points to return. Defaults to 100.

        Returns:
            list[Price]: A list of Price objects representing historical data.
        """
        return self.handler.try_call(lambda w: w.get_historical_prices(asset_id, limit))

    def get_products_aggregated(self, asset_ids: list[str]) -> list[ProductInfo]:
        """
        Gets product information for multiple assets from *all available providers* and *aggregates* the results.

        This method queries all configured sources and then merges the data into a single,
        comprehensive list. Use this for a complete report.
        Warning: This may use a large number of API calls.

        Args:
            asset_ids (list[str]): The list of asset IDs to retrieve information for.

        Returns:
            list[ProductInfo]: A single, aggregated list of ProductInfo objects from all sources.

        Raises:
            Exception: If all providers fail to return results.
        """
        all_products = self.handler.try_call_all(lambda w: w.get_products(asset_ids))
        return ProductInfo.aggregate(all_products)

    def get_historical_prices_aggregated(self, asset_id: str = "BTC", limit: int = 100) -> list[Price]:
        """
        Gets historical price data for a single asset from *all available providers* and *aggregates* the results.

        This method queries all configured sources and then merges the data into a single,
        comprehensive list of price points. Use this for a complete historical analysis.
        Warning: This may use a large number of API calls.

        Args:
            asset_id (str): The asset ID to retrieve price data for. Defaults to "BTC".
            limit (int): The maximum number of price data points to retrieve *from each* provider. Defaults to 100.

        Returns:
            list[Price]: A single, aggregated list of Price objects from all sources.

        Raises:
            Exception: If all providers fail to return results.
        """
        all_prices = self.handler.try_call_all(lambda w: w.get_historical_prices(asset_id, limit))
        return Price.aggregate(all_prices)
