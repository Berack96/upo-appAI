import os
from typing import Any
from binance.client import Client # type: ignore
from app.api.core.markets import ProductInfo, MarketWrapper, Price


def extract_product(currency: str, ticker_data: dict[str, Any]) -> ProductInfo:
    product = ProductInfo()
    product.id = ticker_data.get('symbol', '')
    product.symbol = ticker_data.get('symbol', '').replace(currency, '')
    product.price = float(ticker_data.get('price', 0))
    product.volume_24h = float(ticker_data.get('volume', 0))
    product.currency = currency
    return product

def extract_price(kline_data: list[Any]) -> Price:
    timestamp = kline_data[0]

    price = Price()
    price.open = float(kline_data[1])
    price.high = float(kline_data[2])
    price.low = float(kline_data[3])
    price.close = float(kline_data[4])
    price.volume = float(kline_data[5])
    price.set_timestamp(timestamp_ms=timestamp)
    return price


# Add here eventual other fiat not supported by Binance
FIAT_TO_STABLECOIN = {
    "USD": "USDT",
}

class BinanceWrapper(MarketWrapper):
    """
    Wrapper per le API autenticate di Binance.\n
    Implementa l'interfaccia BaseWrapper per fornire accesso unificato
    ai dati di mercato di Binance tramite le API REST con autenticazione.\n
    https://binance-docs.github.io/apidocs/spot/en/
    """

    def __init__(self, currency: str = "USD"):
        """
        Inizializza il wrapper di Binance con le credenziali API e la valuta di riferimento.
        Alcune valute fiat non sono supportate direttamente da Binance (es. "USD").
        Infatti, se viene fornita una valuta fiat come "USD", questa viene automaticamente convertita in una stablecoin Tether ("USDT") per compatibilità con Binance.
        Args:
            currency (str): Valuta in cui restituire i prezzi. Se "USD" viene fornito, verrà utilizzato "USDT". Default è "USD".
        """
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")

        self.currency = currency if currency not in FIAT_TO_STABLECOIN else FIAT_TO_STABLECOIN[currency]
        self.client = Client(api_key=api_key, api_secret=api_secret)

    def __format_symbol(self, asset_id: str) -> str:
        """
        Formatta l'asset_id nel formato richiesto da Binance.
        """
        return asset_id.replace('-', '') if '-' in asset_id else f"{asset_id}{self.currency}"

    def get_product(self, asset_id: str) -> ProductInfo:
        symbol = self.__format_symbol(asset_id)

        ticker: dict[str, Any] = self.client.get_symbol_ticker(symbol=symbol) # type: ignore
        ticker_24h: dict[str, Any] = self.client.get_ticker(symbol=symbol) # type: ignore
        ticker['volume'] = ticker_24h.get('volume', 0)

        return extract_product(self.currency, ticker)

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        return [ self.get_product(asset_id) for asset_id in asset_ids ]

    def get_historical_prices(self, asset_id: str, limit: int = 100) -> list[Price]:
        symbol = self.__format_symbol(asset_id)

        # Ottiene candele orarie degli ultimi 30 giorni
        klines: list[list[Any]] = self.client.get_historical_klines( # type: ignore
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=limit,
        )
        return [extract_price(kline) for kline in klines]
