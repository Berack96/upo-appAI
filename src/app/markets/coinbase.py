import os

from coinbase.rest import RESTClient

from src.app.markets.base import ProductInfo, BaseWrapper, Price


class CoinBaseWrapper(BaseWrapper):
    """
    Wrapper per le API di Coinbase.
    La documentazione delle API è disponibile qui: https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/introduction
    """
    def __init__(self, api_key:str = None, api_private_key:str = None, currency: str = "USD"):
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

    def get_product(self, asset_id: str) -> ProductInfo:
        asset_id = self.__format(asset_id)
        asset = self.client.get_product(asset_id)
        return ProductInfo.from_coinbase(asset)

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        all_asset_ids = [self.__format(asset_id) for asset_id in asset_ids]
        assets = self.client.get_products(all_asset_ids)
        return [ProductInfo.from_coinbase(asset) for asset in assets.products]

    def get_all_products(self) -> list[ProductInfo]:
        assets = self.client.get_products()
        return [ProductInfo.from_coinbase(asset) for asset in assets.products]

    def get_historical_prices(self, asset_id: str = "BTC") -> list[Price]:
        asset_id = self.__format(asset_id)
        data = self.client.get_candles(product_id=asset_id)
        return [Price.from_coinbase(candle) for candle in data.candles]
