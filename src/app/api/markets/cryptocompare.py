import os
from typing import Any
import requests
from app.api.base.markets import ProductInfo, MarketWrapper, Price


def extract_product(asset_data: dict[str, Any]) -> ProductInfo:
    product = ProductInfo()
    product.id = asset_data.get('FROMSYMBOL', '') + '-' + asset_data.get('TOSYMBOL', '')
    product.symbol = asset_data.get('FROMSYMBOL', '')
    product.price = float(asset_data.get('PRICE', 0))
    product.volume_24h = float(asset_data.get('VOLUME24HOUR', 0))
    assert product.price > 0, "Invalid price data received from CryptoCompare"
    return product

def extract_price(price_data: dict[str, Any]) -> Price:
    timestamp = price_data.get('time', 0)

    price = Price()
    price.high = float(price_data.get('high', 0))
    price.low = float(price_data.get('low', 0))
    price.open = float(price_data.get('open', 0))
    price.close = float(price_data.get('close', 0))
    price.volume = float(price_data.get('volumeto', 0))
    price.set_timestamp(timestamp_s=timestamp)
    return price


BASE_URL = "https://min-api.cryptocompare.com"

class CryptoCompareWrapper(MarketWrapper):
    """
    Wrapper per le API pubbliche di CryptoCompare.
    La documentazione delle API è disponibile qui: https://developers.coindesk.com/documentation/legacy/Price/SingleSymbolPriceEndpoint
    !!ATTENZIONE!! sembra essere una API legacy e potrebbe essere deprecata in futuro.
    """
    def __init__(self, currency:str='USD'):
        api_key = os.getenv("CRYPTOCOMPARE_API_KEY")
        assert api_key, "CRYPTOCOMPARE_API_KEY environment variable not set"

        self.api_key = api_key
        self.currency = currency

    def __request(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if params is None:
            params = {}
        params['api_key'] = self.api_key

        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        return response.json()

    def get_product(self, asset_id: str) -> ProductInfo:
        response = self.__request("/data/pricemultifull", params = {
            "fsyms": asset_id,
            "tsyms": self.currency
        })
        data = response.get('RAW', {}).get(asset_id, {}).get(self.currency, {})
        return extract_product(data)

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        response = self.__request("/data/pricemultifull", params = {
            "fsyms": ",".join(asset_ids),
            "tsyms": self.currency
        })
        assets: list[ProductInfo] = []
        data = response.get('RAW', {})
        for asset_id in asset_ids:
            asset_data = data.get(asset_id, {}).get(self.currency, {})
            assets.append(extract_product(asset_data))
        return assets

    def get_historical_prices(self, asset_id: str, limit: int = 100) -> list[Price]:
        response = self.__request("/data/v2/histohour", params = {
            "fsym": asset_id,
            "tsym": self.currency,
            "limit": limit-1 # because the API returns limit+1 items (limit + current)
        })

        data = response.get('Data', {}).get('Data', [])
        prices = [extract_price(price_data) for price_data in data]
        return prices
