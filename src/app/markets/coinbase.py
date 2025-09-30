import os
from enum import Enum
from datetime import datetime, timedelta
from coinbase.rest import RESTClient
from .base import ProductInfo, BaseWrapper, Price
from .error_handler import retry_on_failure, handle_api_errors, MarketAPIError, RateLimitError


class Granularity(Enum):
    UNKNOWN_GRANULARITY = 0
    ONE_MINUTE = 60
    FIVE_MINUTE = 300
    FIFTEEN_MINUTE = 900
    THIRTY_MINUTE = 1800
    ONE_HOUR = 3600
    TWO_HOUR = 7200
    FOUR_HOUR = 14400
    SIX_HOUR = 21600
    ONE_DAY = 86400

class CoinBaseWrapper(BaseWrapper):
    """
    Wrapper per le API di Coinbase Advanced Trade.\n
    Implementa l'interfaccia BaseWrapper per fornire accesso unificato
    ai dati di mercato di Coinbase tramite le API REST.\n
    https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/introduction
    """

    def __init__(self, currency: str = "USD"):
        api_key = os.getenv("COINBASE_API_KEY")
        assert api_key is not None, "API key is required"

        api_private_key = os.getenv("COINBASE_API_SECRET")
        assert api_private_key is not None, "API private key is required"

        self.currency = currency
        self.client: RESTClient = RESTClient(
            api_key=api_key,
            api_secret=api_private_key
        )

    def __format(self, asset_id: str) -> str:
        return asset_id if '-' in asset_id else f"{asset_id}-{self.currency}"

    def get_product(self, asset_id: str) -> ProductInfo:
        asset_id = self.__format(asset_id)
        asset = self.client.get_product(asset_id)
        return ProductInfo.from_coinbase(asset)

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        all_asset_ids = [self.__format(asset_id) for asset_id in asset_ids]
        assets = self.client.get_products(product_ids=all_asset_ids)
        return [ProductInfo.from_coinbase(asset) for asset in assets.products]

    def get_all_products(self) -> list[ProductInfo]:
        assets = self.client.get_products()
        return [ProductInfo.from_coinbase_product(asset) for asset in assets.products]

    def get_historical_prices(self, asset_id: str = "BTC", limit: int = 100) -> list[Price]:
        asset_id = self.__format(asset_id)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=14)

        data = self.client.get_candles(
            product_id=asset_id,
            granularity=Granularity.ONE_HOUR.name,
            start=str(int(start_time.timestamp())),
            end=str(int(end_time.timestamp())),
            limit=limit
        )
        return [Price.from_coinbase(candle) for candle in data.candles]
