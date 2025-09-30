import os
from typing import Optional
from datetime import datetime, timedelta
from coinbase.rest import RESTClient
from .base import ProductInfo, BaseWrapper, Price
from .error_handler import retry_on_failure, handle_api_errors, MarketAPIError, RateLimitError

class CoinBaseWrapper(BaseWrapper):
    """
    Wrapper per le API di Coinbase Advanced Trade.
    
    Implementa l'interfaccia BaseWrapper per fornire accesso unificato
    ai dati di mercato di Coinbase tramite le API REST.
    
    La documentazione delle API è disponibile qui: 
    https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/introduction
    """
    def __init__(self, api_key: Optional[str] = None, api_private_key: Optional[str] = None, currency: str = "USD"):
        if api_key is None:
            api_key = os.getenv("COINBASE_API_KEY")
        assert api_key is not None, "API key is required"

        if api_private_key is None:
            api_private_key = os.getenv("COINBASE_API_SECRET")
        assert api_private_key is not None, "API private key is required"

        self.currency = currency
        self.client: RESTClient = RESTClient(
            api_key=api_key,
            api_secret=api_private_key
        )

    def __format(self, asset_id: str) -> str:
        return asset_id if '-' in asset_id else f"{asset_id}-{self.currency}"

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_product(self, asset_id: str) -> ProductInfo:
        asset_id = self.__format(asset_id)
        asset = self.client.get_product(asset_id)
        return ProductInfo.from_coinbase(asset)

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        all_asset_ids = [self.__format(asset_id) for asset_id in asset_ids]
        assets = self.client.get_products(product_ids=all_asset_ids)
        if assets.products:
            return [ProductInfo.from_coinbase_product(asset) for asset in assets.products]
        return []

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_all_products(self) -> list[ProductInfo]:
        assets = self.client.get_products()
        if assets.products:
            return [ProductInfo.from_coinbase_product(asset) for asset in assets.products]
        return []

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_historical_prices(self, asset_id: str = "BTC") -> list[Price]:
        asset_id = self.__format(asset_id)
        # Get last 14 days of hourly data (14*24 = 336 candles, within 350 limit)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=14)
        
        # Convert to UNIX timestamps as strings (required by Coinbase API)
        start_timestamp = str(int(start_time.timestamp()))
        end_timestamp = str(int(end_time.timestamp()))
        
        data = self.client.get_candles(
            product_id=asset_id,
            start=start_timestamp,
            end=end_timestamp,
            granularity="ONE_HOUR",
            limit=350  # Explicitly set the limit
        )
        if data.candles:
            return [Price.from_coinbase(candle) for candle in data.candles]
        return []
