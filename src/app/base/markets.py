from pydantic import BaseModel


class ProductInfo(BaseModel):
    """
    Informazioni sul prodotto, come ottenute dalle API di mercato.
    Implementa i metodi di conversione dai dati grezzi delle API.
    """
    id: str = ""
    symbol: str = ""
    price: float = 0.0
    volume_24h: float = 0.0
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
    timestamp_ms: int = 0  # Timestamp in milliseconds

class MarketWrapper:
    """
    Base class for market API wrappers.
    All market API wrappers should inherit from this class and implement the methods.
    """

    def get_product(self, asset_id: str) -> ProductInfo:
        """
        Get product information for a specific asset ID.
        Args:
            asset_id (str): The asset ID to retrieve information for.
        Returns:
            ProductInfo: An object containing product information.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        """
        Get product information for multiple asset IDs.
        Args:
            asset_ids (list[str]): The list of asset IDs to retrieve information for.
        Returns:
            list[ProductInfo]: A list of objects containing product information.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_historical_prices(self, asset_id: str, limit: int = 100) -> list[Price]:
        """
        Get historical price data for a specific asset ID.
        Args:
            asset_id (str): The asset ID to retrieve price data for.
            limit (int): The maximum number of price data points to return.
        Returns:
            list[Price]: A list of Price objects.
        """
        raise NotImplementedError("This method should be overridden by subclasses")
