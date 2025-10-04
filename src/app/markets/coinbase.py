import os
from enum import Enum
from datetime import datetime, timedelta
from coinbase.rest import RESTClient # type: ignore
from coinbase.rest.types.product_types import Candle, GetProductResponse, Product # type: ignore
from app.markets.base import ProductInfo, MarketWrapper, Price


def extract_product(product_data: GetProductResponse | Product) -> ProductInfo:
    product = ProductInfo()
    product.id = product_data.product_id or ""
    product.symbol = product_data.base_currency_id or ""
    product.price = float(product_data.price) if product_data.price else 0.0
    product.volume_24h = float(product_data.volume_24h) if product_data.volume_24h else 0.0
    return product

def extract_price(candle_data: Candle) -> Price:
    price = Price()
    price.high = float(candle_data.high) if candle_data.high else 0.0
    price.low = float(candle_data.low) if candle_data.low else 0.0
    price.open = float(candle_data.open) if candle_data.open else 0.0
    price.close = float(candle_data.close) if candle_data.close else 0.0
    price.volume = float(candle_data.volume) if candle_data.volume else 0.0
    price.timestamp_ms = int(candle_data.start) * 1000 if candle_data.start else 0
    return price


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

class CoinBaseWrapper(MarketWrapper):
    """
    Wrapper per le API di Coinbase Advanced Trade.\n
    Implementa l'interfaccia BaseWrapper per fornire accesso unificato
    ai dati di mercato di Coinbase tramite le API REST.\n
    https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/introduction
    """

    def __init__(self, currency: str = "USD"):
        api_key = os.getenv("COINBASE_API_KEY")
        assert api_key, "COINBASE_API_KEY environment variable not set"

        api_private_key = os.getenv("COINBASE_API_SECRET")
        assert api_private_key, "COINBASE_API_SECRET environment variable not set"

        self.currency = currency
        self.client: RESTClient = RESTClient(
            api_key=api_key,
            api_secret=api_private_key
        )

    def __format(self, asset_id: str) -> str:
        return asset_id if '-' in asset_id else f"{asset_id}-{self.currency}"

    def get_product(self, asset_id: str) -> ProductInfo:
        asset_id = self.__format(asset_id)
        asset = self.client.get_product(asset_id) # type: ignore
        return extract_product(asset)

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        all_asset_ids = [self.__format(asset_id) for asset_id in asset_ids]
        assets = self.client.get_products(product_ids=all_asset_ids) # type: ignore
        assert assets.products is not None, "No products data received from Coinbase"
        return [extract_product(asset) for asset in assets.products]

    def get_historical_prices(self, asset_id: str, limit: int = 100) -> list[Price]:
        asset_id = self.__format(asset_id)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=14)

        data = self.client.get_candles( # type: ignore
            product_id=asset_id,
            granularity=Granularity.ONE_HOUR.name,
            start=str(int(start_time.timestamp())),
            end=str(int(end_time.timestamp())),
            limit=limit
        )
        assert data.candles is not None, "No candles data received from Coinbase"
        return [extract_price(candle) for candle in data.candles]
