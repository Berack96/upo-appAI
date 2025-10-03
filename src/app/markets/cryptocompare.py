import os
import requests
from typing import Optional, Dict, Any
from app.markets.base import ProductInfo, BaseWrapper, Price
from app.markets.error_handler import retry_on_failure, handle_api_errors, MarketAPIError

BASE_URL = "https://min-api.cryptocompare.com"

class CryptoCompareWrapper(BaseWrapper):
    """
    Wrapper per le API pubbliche di CryptoCompare.
    La documentazione delle API è disponibile qui: https://developers.coindesk.com/documentation/legacy/Price/SingleSymbolPriceEndpoint
    !!ATTENZIONE!! sembra essere una API legacy e potrebbe essere deprecata in futuro.
    """
    def __init__(self, api_key: Optional[str] = None, currency: str = 'USD'):
        if api_key is None:
            api_key = os.getenv("CRYPTOCOMPARE_API_KEY")
        assert api_key is not None, "API key is required"

        self.api_key = api_key
        self.currency = currency

    def __request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if params is None:
            params = {}
        params['api_key'] = self.api_key

        response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        return response.json()

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_product(self, asset_id: str) -> ProductInfo:
        response = self.__request("/data/pricemultifull", params = {
            "fsyms": asset_id,
            "tsyms": self.currency
        })
        data = response.get('RAW', {}).get(asset_id, {}).get(self.currency, {})
        return ProductInfo.from_cryptocompare(data)

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
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

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_all_products(self) -> list[ProductInfo]:
        """
        Workaround per CryptoCompare: utilizza una lista predefinita di asset popolari
        poiché l'API non fornisce un endpoint per recuperare tutti i prodotti.
        """
        # Lista di asset popolari supportati da CryptoCompare
        popular_assets = [
            "BTC", "ETH", "ADA", "DOT", "LINK", "LTC", "XRP", "BCH", "BNB", "SOL",
            "MATIC", "AVAX", "ATOM", "UNI", "DOGE", "SHIB", "TRX", "ETC", "FIL", "XLM"
        ]
        
        try:
            # Utilizza get_products per recuperare i dati di tutti gli asset popolari
            return self.get_products(popular_assets)
        except Exception as e:
            # Fallback: prova con un set ridotto di asset principali
            main_assets = ["BTC", "ETH", "ADA", "DOT", "LINK"]
            try:
                return self.get_products(main_assets)
            except Exception as fallback_error:
                # Se anche il fallback fallisce, solleva l'errore originale con informazioni aggiuntive
                raise NotImplementedError(
                    f"CryptoCompare get_all_products() workaround failed. "
                    f"Original error: {str(e)}, Fallback error: {str(fallback_error)}"
                )

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_historical_prices(self, asset_id: str = "BTC", day_back: int = 10) -> list[Price]:
        assert day_back <= 30, "day_back should be less than or equal to 30"
        response = self.__request("/data/v2/histohour", params = {
            "fsym": asset_id,
            "tsym": self.currency,
            "limit": day_back * 24
        })

        data = response.get('Data', {}).get('Data', [])
        prices = [Price.from_cryptocompare(price_data) for price_data in data]
        return prices
