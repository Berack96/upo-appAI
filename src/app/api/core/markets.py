import statistics
from pydantic import BaseModel
from app.api.core import unified_timestamp


class ProductInfo(BaseModel):
    """
    Product information as obtained from market APIs.
    Implements conversion methods from raw API data.
    """
    id: str = ""
    symbol: str = ""
    price: float = 0.0
    volume_24h: float = 0.0
    currency: str = ""
    provider: str = ""

    @staticmethod
    def aggregate_multi_assets(products: dict[str, list['ProductInfo']]) -> list['ProductInfo']:
        """
        Aggregates a list of ProductInfo by symbol across different providers.
        Args:
            products (dict[str, list[ProductInfo]]): Map provider -> list of ProductInfo
        Returns:
            list[ProductInfo]: List of ProductInfo aggregated by symbol, combining data from all providers
        """

        # Costruzione mappa symbol -> lista di ProductInfo (da tutti i provider)
        symbols_infos: dict[str, list[ProductInfo]] = {}
        for provider_name, product_list in products.items():
            for product in product_list:
                # Assicuriamo che il provider sia impostato
                if not product.provider:
                    product.provider = provider_name
                symbols_infos.setdefault(product.symbol, []).append(product)

        # Aggregazione per ogni symbol
        aggregated_products: list[ProductInfo] = []
        for symbol, product_list in symbols_infos.items():
            product = ProductInfo()

            product.id = f"{symbol}_AGGREGATED"
            product.symbol = symbol
            product.currency = next((p.currency for p in product_list if p.currency), "")
            
            # Raccogliamo i provider che hanno fornito dati
            providers = [p.provider for p in product_list if p.provider]
            product.provider = ", ".join(set(providers)) if providers else "AGGREGATED"

            # Calcolo del volume medio
            volume_sum = sum(p.volume_24h for p in product_list if p.volume_24h > 0)
            product.volume_24h = volume_sum / len(product_list) if product_list else 0.0

            # Calcolo del prezzo pesato per volume (VWAP - Volume Weighted Average Price)
            if volume_sum > 0:
                prices_weighted = sum(p.price * p.volume_24h for p in product_list if p.volume_24h > 0)
                product.price = prices_weighted / volume_sum
            else:
                # Se non c'è volume, facciamo una media semplice dei prezzi
                valid_prices = [p.price for p in product_list if p.price > 0]
                product.price = sum(valid_prices) / len(valid_prices) if valid_prices else 0.0

            aggregated_products.append(product)
        return aggregated_products
    
    @staticmethod
    def aggregate_single_asset(assets: list['ProductInfo'] | dict[str, 'ProductInfo'] | dict[str, list['ProductInfo']]) -> 'ProductInfo':
        """
        Aggregates an asset across different exchanges.
        Args:
            assets: Can be:
                - list[ProductInfo]: Direct list of products
                - dict[str, ProductInfo]: Map provider -> ProductInfo (from WrapperHandler.try_call_all)
                - dict[str, list[ProductInfo]]: Map provider -> list of ProductInfo
        Returns:
            ProductInfo: Aggregated ProductInfo combining data from all exchanges
        """

        # Defensive handling: normalize to a flat list of ProductInfo
        if not assets:
            raise ValueError("aggregate_single_asset requires at least one ProductInfo")

        # Normalize to a flat list of ProductInfo
        if isinstance(assets, dict):
            # Check if dict values are ProductInfo or list[ProductInfo]
            first_value = next(iter(assets.values())) if assets else None
            if first_value and isinstance(first_value, list):
                # dict[str, list[ProductInfo]] -> flatten
                assets_list = [product for product_list in assets.values() for product in product_list]
            else:
                # dict[str, ProductInfo] -> extract values
                assets_list = list(assets.values())
        elif isinstance(assets, list) and assets and isinstance(assets[0], list):
            # Flatten list[list[ProductInfo]] -> list[ProductInfo]
            assets_list = [product for sublist in assets for product in sublist]
        else:
            # Already a flat list of ProductInfo
            assets_list = list(assets)

        if not assets_list:
            raise ValueError("aggregate_single_asset requires at least one ProductInfo")

        # Aggregazione per ogni Exchange
        aggregated: ProductInfo = ProductInfo()
        first = assets_list[0]
        aggregated.id = f"{first.symbol}_AGGREGATED"
        aggregated.symbol = first.symbol
        aggregated.currency = next((p.currency for p in assets_list if p.currency), "")
        
        # Raccogliamo i provider che hanno fornito dati
        providers = [p.provider for p in assets_list if p.provider]
        aggregated.provider = ", ".join(set(providers)) if providers else "AGGREGATED"
        
        # Calcolo del volume medio
        volume_sum = sum(p.volume_24h for p in assets_list if p.volume_24h > 0)
        aggregated.volume_24h = volume_sum / len(assets_list) if assets_list else 0.0
        # Calcolo del prezzo pesato per volume (VWAP - Volume Weighted Average Price)
        if volume_sum > 0:
            prices_weighted = sum(p.price * p.volume_24h for p in assets_list if p.volume_24h > 0)
            aggregated.price = prices_weighted / volume_sum
        else:
            # Se non c'è volume, facciamo una media semplice dei prezzi
            valid_prices = [p.price for p in assets_list if p.price > 0]
            aggregated.price = sum(valid_prices) / len(valid_prices) if valid_prices else 0.0

        return aggregated



class Price(BaseModel):
    """
    Represents price data for an asset as obtained from market APIs.
    Implements conversion methods from raw API data.
    """
    high: float = 0.0
    low: float = 0.0
    open: float = 0.0
    close: float = 0.0
    volume: float = 0.0
    timestamp: str = ""
    """Timestamp in format YYYY-MM-DD HH:MM"""

    def set_timestamp(self, timestamp_ms: int | None = None, timestamp_s: int | None = None) -> None:
        """ Use the unified_timestamp function to set the timestamp."""
        self.timestamp = unified_timestamp(timestamp_ms, timestamp_s)

    @staticmethod
    def aggregate(prices: dict[str, list['Price']]) -> list['Price']:
        """
        Aggregates historical prices for the same symbol by calculating the mean.
        Args:
            prices (dict[str, list[Price]]): Map provider -> list of Price.
                The map must contain only Price objects for the same symbol.
        Returns:
            list[Price]: List of Price objects aggregated by timestamp.
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

class MarketWrapper:
    """
    Base class for market API wrappers.
    All market API wrappers should inherit from this class and implement the methods.
    Provides interface for retrieving product and price information from market APIs.
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
