import os
import requests
from typing import Optional, Dict, Any
from .base import ProductInfo, BaseWrapper, Price


def get_product(asset_data: dict) -> 'ProductInfo':
    product = ProductInfo()
    product.id = asset_data['FROMSYMBOL'] + '-' + asset_data['TOSYMBOL']
    product.symbol = asset_data['FROMSYMBOL']
    product.price = float(asset_data['PRICE'])
    product.volume_24h = float(asset_data['VOLUME24HOUR'])
    product.status = "" # Cryptocompare does not provide status
    return product

def get_price(price_data: dict) -> 'Price':
    price = Price()
    price.high = float(price_data['high'])
    price.low = float(price_data['low'])
    price.open = float(price_data['open'])
    price.close = float(price_data['close'])
    price.volume = float(price_data['volumeto'])
    price.time = str(price_data['time'])
    return price


BASE_URL = "https://min-api.cryptocompare.com"

class CryptoCompareWrapper(BaseWrapper):
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

    def __request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
        return get_product(data)

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        response = self.__request("/data/pricemultifull", params = {
            "fsyms": ",".join(asset_ids),
            "tsyms": self.currency
        })
        assets = []
        data = response.get('RAW', {})
        for asset_id in asset_ids:
            asset_data = data.get(asset_id, {}).get(self.currency, {})
            assets.append(get_product(asset_data))
        return assets

    def get_historical_prices(self, asset_id: str, limit: int = 100) -> list[dict]:
        response = self.__request("/data/v2/histohour", params = {
            "fsym": asset_id,
            "tsym": self.currency,
            "limit": limit-1 # because the API returns limit+1 items (limit + current)
        })

        data = response.get('Data', {}).get('Data', [])
        prices = [get_price(price_data) for price_data in data]
        return prices
