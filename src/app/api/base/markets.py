import statistics
from datetime import datetime
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
    currency: str = ""

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
    timestamp: str = ""
    """Timestamp con formato YYYY-MM-DD HH:MM"""

    def set_timestamp(self, timestamp_ms: int | None = None, timestamp_s: int | None = None) -> None:
        """
        Imposta il timestamp a partire da millisecondi o secondi.
        IL timestamp viene salvato come stringa formattata 'YYYY-MM-DD HH:MM'.
        Args:
            timestamp_ms: Timestamp in millisecondi.
            timestamp_s: Timestamp in secondi.
        Raises:
        """
        if timestamp_ms is not None:
            timestamp = timestamp_ms // 1000
        elif timestamp_s is not None:
            timestamp = timestamp_s
        else:
            raise ValueError("Either timestamp_ms or timestamp_s must be provided")
        assert timestamp > 0, "Invalid timestamp data received"

        self.timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

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


def aggregate_history_prices(prices: dict[str, list[Price]]) -> list[Price]:
    """
    Aggrega i prezzi storici per symbol calcolando la media.
    Args:
        prices (dict[str, list[Price]]): Mappa provider -> lista di Price
    Returns:
        list[Price]: Lista di Price aggregati per timestamp
    """

    # Costruiamo una mappa timestamp -> lista di Price
    timestamped_prices: dict[str, list[Price]] = {}
    for _, price_list in prices.items():
        for price in price_list:
            timestamped_prices.setdefault(price.timestamp, []).append(price)

    # Ora aggregiamo i prezzi per ogni timestamp
    aggregated_prices: list[Price] = []
    for time, price_list in timestamped_prices.items():
        price = Price()
        price.timestamp = time
        price.high = statistics.mean([p.high for p in price_list])
        price.low = statistics.mean([p.low for p in price_list])
        price.open = statistics.mean([p.open for p in price_list])
        price.close = statistics.mean([p.close for p in price_list])
        price.volume = statistics.mean([p.volume for p in price_list])
        aggregated_prices.append(price)
    return aggregated_prices

def aggregate_product_info(products: dict[str, list[ProductInfo]]) -> list[ProductInfo]:
    """
    Aggrega una lista di ProductInfo per symbol.
    Args:
        products (dict[str, list[ProductInfo]]): Mappa provider -> lista di ProductInfo
    Returns:
        list[ProductInfo]: Lista di ProductInfo aggregati per symbol
    """

    # Costruzione mappa symbol -> lista di ProductInfo
    symbols_infos: dict[str, list[ProductInfo]] = {}
    for _, product_list in products.items():
        for product in product_list:
            symbols_infos.setdefault(product.symbol, []).append(product)

    # Aggregazione per ogni symbol
    aggregated_products: list[ProductInfo] = []
    for symbol, product_list in symbols_infos.items():
        product = ProductInfo()

        product.id = f"{symbol}_AGGREGATED"
        product.symbol = symbol
        product.currency = next(p.currency for p in product_list if p.currency)

        volume_sum = sum(p.volume_24h for p in product_list)
        product.volume_24h = volume_sum / len(product_list) if product_list else 0.0

        prices = sum(p.price * p.volume_24h for p in product_list)
        product.price = (prices / volume_sum) if volume_sum > 0 else 0.0

        aggregated_products.append(product)
    return aggregated_products

