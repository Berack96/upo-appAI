from agno.tools import Toolkit
from app.api.wrapper_handler import WrapperHandler
from app.api.core.markets import MarketWrapper, Price, ProductInfo
from app.api.markets import BinanceWrapper, CoinBaseWrapper, CryptoCompareWrapper, YFinanceWrapper
from app.configs import AppConfig

class MarketAPIsTool(MarketWrapper, Toolkit):
    """
    Class that aggregates multiple market API wrappers and manages them using WrapperHandler.
    This class supports retrieving product information and historical prices.
    This class can also aggregate data from multiple sources to provide a more comprehensive view of the market.
    Providers can be configured in configs.yaml under api.market_providers.
    """

    def __init__(self):
        """
        Initialize the MarketAPIsTool with market API wrappers configured in configs.yaml.
        The order of wrappers is determined by the api.market_providers list in the configuration.
        """
        config = AppConfig()

        self.handler = WrapperHandler.build_wrappers(
            constructors=[BinanceWrapper, YFinanceWrapper, CoinBaseWrapper, CryptoCompareWrapper],
            filters=config.api.market_providers,
            try_per_wrapper=config.api.retry_attempts,
            retry_delay=config.api.retry_delay_seconds
        )

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
        return self.handler.try_call(lambda w: w.get_product(asset_id))
    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        return self.handler.try_call(lambda w: w.get_products(asset_ids))
    def get_historical_prices(self, asset_id: str, limit: int = 100) -> list[Price]:
        return self.handler.try_call(lambda w: w.get_historical_prices(asset_id, limit))


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
        all_products = self.handler.try_call_all(lambda w: w.get_products(asset_ids))
        return ProductInfo.aggregate(all_products)

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
        all_prices = self.handler.try_call_all(lambda w: w.get_historical_prices(asset_id, limit))
        return Price.aggregate(all_prices)
