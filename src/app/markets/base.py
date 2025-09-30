
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
    def get_historical_prices(self, asset_id: str = "BTC", limit: int = 100) -> list['Price']:
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
