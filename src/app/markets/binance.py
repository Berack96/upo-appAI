import os
from binance.client import Client
from app.markets.base import ProductInfo, BaseWrapper, Price


def extract_product(currency: str, ticker_data: dict[str, str]) -> ProductInfo:
    product = ProductInfo()
    product.id = ticker_data.get('symbol')
    product.symbol = ticker_data.get('symbol', '').replace(currency, '')
    product.price = float(ticker_data.get('price', 0))
    product.volume_24h = float(ticker_data.get('volume', 0))
    product.quote_currency = currency
    return product

def extract_price(kline_data: list) -> Price:
    price = Price()
    price.open = float(kline_data[1])
    price.high = float(kline_data[2])
    price.low = float(kline_data[3])
    price.close = float(kline_data[4])
    price.volume = float(kline_data[5])
    price.timestamp_ms = kline_data[0]
    return price

class BinanceWrapper(BaseWrapper):
    """
    Wrapper per le API autenticate di Binance.\n
    Implementa l'interfaccia BaseWrapper per fornire accesso unificato
    ai dati di mercato di Binance tramite le API REST con autenticazione.\n
    https://binance-docs.github.io/apidocs/spot/en/
    """

    def __init__(self, currency: str = "USDT"):
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")

        self.currency = currency
        self.client = Client(api_key=api_key, api_secret=api_secret)

    def __format_symbol(self, asset_id: str) -> str:
        """
        Formatta l'asset_id nel formato richiesto da Binance.
        """
        return asset_id.replace('-', '') if '-' in asset_id else f"{asset_id}{self.currency}"

    def get_product(self, asset_id: str) -> ProductInfo:
        symbol = self.__format_symbol(asset_id)

        ticker = self.client.get_symbol_ticker(symbol=symbol)
        ticker_24h = self.client.get_ticker(symbol=symbol)
        ticker['volume'] = ticker_24h.get('volume', 0)  # Aggiunge volume 24h ai dati del ticker

        return extract_product(self.currency, ticker)

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        symbols = [self.__format_symbol(asset_id) for asset_id in asset_ids]
        symbols_str = f"[\"{'","'.join(symbols)}\"]"

        tickers = self.client.get_symbol_ticker(symbols=symbols_str)
        tickers_24h = self.client.get_ticker(symbols=symbols_str) # un po brutale, ma va bene così
        for t, t24 in zip(tickers, tickers_24h):
            t['volume'] = t24.get('volume', 0)

        return [extract_product(self.currency, ticker) for ticker in tickers]

    def get_historical_prices(self, asset_id: str = "BTC", limit: int = 100) -> list[Price]:
        symbol = self.__format_symbol(asset_id)

        # Ottiene candele orarie degli ultimi 30 giorni
        klines = self.client.get_historical_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=limit,
        )
        return [extract_price(kline) for kline in klines]

