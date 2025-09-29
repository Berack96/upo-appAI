from coinbase.rest.types.product_types import Candle, GetProductResponse, Product
from pydantic import BaseModel

class BaseWrapper:
    """
    Interfaccia per i wrapper delle API di mercato.
    Implementa i metodi di base che ogni wrapper deve avere.
    """
    def get_product(self, asset_id: str) -> 'ProductInfo':
        raise NotImplementedError
    def get_products(self, asset_ids: list[str]) -> list['ProductInfo']:
        raise NotImplementedError
    def get_all_products(self) -> list['ProductInfo']:
        raise NotImplementedError
    def get_historical_prices(self, asset_id: str = "BTC") -> list['Price']:
        raise NotImplementedError

class ProductInfo(BaseModel):
    """
    Informazioni sul prodotto, come ottenute dalle API di mercato.
    Implementa i metodi di conversione dai dati grezzi delle API.
    """
    id: str = ""
    symbol: str = ""
    price: float = 0.0
    volume_24h: float = 0.0
    status: str = ""
    quote_currency: str = ""

    @staticmethod
    def from_coinbase(product_data: GetProductResponse) -> 'ProductInfo':
        product = ProductInfo()
        product.id = product_data.product_id or ""
        product.symbol = product_data.base_currency_id or ""
        product.price = float(product_data.price) if product_data.price else 0.0
        product.volume_24h = float(product_data.volume_24h) if product_data.volume_24h else 0.0
        # TODO Check what status means in Coinbase
        product.status = product_data.status or ""
        return product

    @staticmethod
    def from_coinbase_product(product_data: Product) -> 'ProductInfo':
        product = ProductInfo()
        product.id = product_data.product_id or ""
        product.symbol = product_data.base_currency_id or ""
        product.price = float(product_data.price) if product_data.price else 0.0
        product.volume_24h = float(product_data.volume_24h) if product_data.volume_24h else 0.0
        product.status = product_data.status or ""
        return product

    @staticmethod
    def from_cryptocompare(asset_data: dict) -> 'ProductInfo':
        product = ProductInfo()
        product.id = asset_data['FROMSYMBOL'] + '-' + asset_data['TOSYMBOL']
        product.symbol = asset_data['FROMSYMBOL']
        product.price = float(asset_data['PRICE'])
        product.volume_24h = float(asset_data['VOLUME24HOUR'])
        product.status = "" # Cryptocompare does not provide status
        return product

    @staticmethod
    def from_binance(ticker_data: dict, ticker_24h_data: dict) -> 'ProductInfo':
        """
        Crea un oggetto ProductInfo da dati Binance.
        
        Args:
            ticker_data: Dati del ticker di prezzo
            ticker_24h_data: Dati del ticker 24h
        
        Returns:
            Oggetto ProductInfo
        """
        product = ProductInfo()
        product.id = ticker_data['symbol']
        product.symbol = ticker_data['symbol'].replace('USDT', '').replace('BUSD', '')
        product.price = float(ticker_data['price'])
        product.volume_24h = float(ticker_24h_data['volume'])
        product.status = "TRADING"  # Binance non fornisce status esplicito
        product.quote_currency = "USDT"  # Assumiamo USDT come default
        return product

class Price(BaseModel):
    """
    Rappresenta i dati di prezzo per un asset, come ottenuti dalle API di mercato.
    Implementa i metodi di conversione dai dati grezzi delle API.
    """
    high: float = 0.0
    low: float = 0.0
    open: float = 0.0
    close: float = 0.0
    volume: float = 0.0
    time: str = ""

    @staticmethod
    def from_coinbase(candle_data: Candle) -> 'Price':
        price = Price()
        price.high = float(candle_data.high) if candle_data.high else 0.0
        price.low = float(candle_data.low) if candle_data.low else 0.0
        price.open = float(candle_data.open) if candle_data.open else 0.0
        price.close = float(candle_data.close) if candle_data.close else 0.0
        price.volume = float(candle_data.volume) if candle_data.volume else 0.0
        price.time = str(candle_data.start) if candle_data.start else ""
        return price

    @staticmethod
    def from_cryptocompare(price_data: dict) -> 'Price':
        price = Price()
        price.high = float(price_data['high'])
        price.low = float(price_data['low'])
        price.open = float(price_data['open'])
        price.close = float(price_data['close'])
        price.volume = float(price_data['volumeto'])
        price.time = str(price_data['time'])
        return price
