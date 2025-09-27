import os
import requests
from app.markets.base import ProductInfo, BaseWrapper, Price

BASE_URL = "https://min-api.cryptocompare.com"

class CryptoCompareWrapper(BaseWrapper):
    """
    Wrapper per le API pubbliche di CryptoCompare.
    La documentazione delle API è disponibile qui: https://developers.coindesk.com/documentation/legacy/Price/SingleSymbolPriceEndpoint
    !!ATTENZIONE!! sembra essere una API legacy e potrebbe essere deprecata in futuro.
    """
    def __init__(self, api_key:str = None, currency:str='USD'):
        if api_key is None:
            api_key = os.getenv("CRYPTOCOMPARE_API_KEY")
        assert api_key is not None, "API key is required"

        self.api_key = api_key
        self.currency = currency

    def __request(self, endpoint: str, params: dict = None) -> dict:
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
        return ProductInfo.from_cryptocompare(data)

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        response = self.__request("/data/pricemultifull", params = {
            "fsyms": ",".join(asset_ids),
            "tsyms": self.currency
        })
        assets = []
        data = response.get('RAW', {})
        for asset_id in asset_ids:
            asset_data = data.get(asset_id, {}).get(self.currency, {})
            assets.append(ProductInfo.from_cryptocompare(asset_data))
        return assets

    def get_all_products(self) -> list[ProductInfo]:
        raise NotImplementedError("CryptoCompare does not support fetching all assets")

    def get_historical_prices(self, asset_id: str, day_back: int = 10) -> list[dict]:
        assert day_back <= 30, "day_back should be less than or equal to 30"
        response = self.__request("/data/v2/histohour", params = {
            "fsym": asset_id,
            "tsym": self.currency,
            "limit": day_back * 24
        })

        data = response.get('Data', {}).get('Data', [])
        prices = [Price.from_cryptocompare(price_data) for price_data in data]
        return prices
