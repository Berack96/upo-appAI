from typing import List, Optional, Dict, Any
from app.markets.base import ProductInfo, Price
from app.utils.aggregated_models import AggregatedProductInfo

class MarketDataAggregator:
    """
    Aggregatore di dati di mercato che mantiene la trasparenza per l'utente.

    Compone MarketAPIs per fornire gli stessi metodi, ma restituisce dati aggregati
    da tutte le fonti disponibili. L'utente finale non vede la complessità.
    """

    def __init__(self, currency: str = "USD"):
        # Import lazy per evitare circular import
        from app.markets import MarketAPIsTool
        self._market_apis = MarketAPIsTool(currency)
        self._aggregation_enabled = True

    def get_product(self, asset_id: str) -> ProductInfo:
        """
        Override che aggrega dati da tutte le fonti disponibili.
        Per l'utente sembra un normale ProductInfo.
        """
        if not self._aggregation_enabled:
            return self._market_apis.get_product(asset_id)

        # Raccogli dati da tutte le fonti
        try:
            raw_results = self.wrappers.try_call_all(
                lambda wrapper: wrapper.get_product(asset_id)
            )

            # Converti in ProductInfo se necessario
            products = []
            for wrapper_class, result in raw_results.items():
                if isinstance(result, ProductInfo):
                    products.append(result)
                elif isinstance(result, dict):
                    # Converti dizionario in ProductInfo
                    products.append(ProductInfo(**result))

            if not products:
                raise Exception("Nessun dato disponibile")

            # Aggrega i risultati
            aggregated = AggregatedProductInfo.from_multiple_sources(products)

            # Restituisci come ProductInfo normale (nascondi la complessità)
            return ProductInfo(**aggregated.dict(exclude={"_metadata", "_source_data"}))

        except Exception as e:
            # Fallback: usa il comportamento normale se l'aggregazione fallisce
            return self._market_apis.get_product(asset_id)

    def get_products(self, asset_ids: List[str]) -> List[ProductInfo]:
        """
        Aggrega dati per multiple asset.
        """
        if not self._aggregation_enabled:
            return self._market_apis.get_products(asset_ids)

        aggregated_products = []

        for asset_id in asset_ids:
            try:
                product = self.get_product(asset_id)
                aggregated_products.append(product)
            except Exception as e:
                # Salta asset che non riescono ad aggregare
                continue

        return aggregated_products

    def get_all_products(self) -> List[ProductInfo]:
        """
        Aggrega tutti i prodotti disponibili.
        """
        if not self._aggregation_enabled:
            return self._market_apis.get_all_products()

        # Raccogli tutti i prodotti da tutte le fonti
        try:
            all_products_by_source = self.wrappers.try_call_all(
                lambda wrapper: wrapper.get_all_products()
            )

            # Raggruppa per symbol per aggregare
            symbol_groups = {}
            for wrapper_class, products in all_products_by_source.items():
                if not isinstance(products, list):
                    continue

                for product in products:
                    if isinstance(product, dict):
                        product = ProductInfo(**product)

                    if product.symbol not in symbol_groups:
                        symbol_groups[product.symbol] = []
                    symbol_groups[product.symbol].append(product)

            # Aggrega ogni gruppo
            aggregated_products = []
            for symbol, products in symbol_groups.items():
                try:
                    aggregated = AggregatedProductInfo.from_multiple_sources(products)
                    # Restituisci come ProductInfo normale
                    aggregated_products.append(
                        ProductInfo(**aggregated.dict(exclude={"_metadata", "_source_data"}))
                    )
                except Exception:
                    # Se l'aggregazione fallisce, usa il primo disponibile
                    if products:
                        aggregated_products.append(products[0])

            return aggregated_products

        except Exception as e:
            # Fallback: usa il comportamento normale
            return self._market_apis.get_all_products()

    def get_historical_prices(self, asset_id: str = "BTC", limit: int = 100) -> List[Price]:
        """
        Per i dati storici, usa una strategia diversa:
        prendi i dati dalla fonte più affidabile o aggrega se possibile.
        """
        if not self._aggregation_enabled:
            return self._market_apis.get_historical_prices(asset_id, limit)

        # Per dati storici, usa il primo wrapper che funziona
        # (l'aggregazione di dati storici è più complessa)
        try:
            return self.wrappers.try_call(
                lambda wrapper: wrapper.get_historical_prices(asset_id, limit)
            )
        except Exception as e:
            # Fallback: usa il comportamento normale
            return self._market_apis.get_historical_prices(asset_id, limit)

    def enable_aggregation(self, enabled: bool = True):
        """Abilita o disabilita l'aggregazione"""
        self._aggregation_enabled = enabled

    def is_aggregation_enabled(self) -> bool:
        """Controlla se l'aggregazione è abilitata"""
        return self._aggregation_enabled

    # Metodi proxy per completare l'interfaccia BaseWrapper
    @property
    def wrappers(self):
        """Accesso al wrapper handler per compatibilità"""
        return self._market_apis.wrappers

    def get_aggregated_product_with_debug(self, asset_id: str) -> Dict[str, Any]:
        """
        Metodo speciale per debugging: restituisce dati aggregati con metadati.
        Usato solo per testing e monitoraggio.
        """
        try:
            raw_results = self.wrappers.try_call_all(
                lambda wrapper: wrapper.get_product(asset_id)
            )

            products = []
            for wrapper_class, result in raw_results.items():
                if isinstance(result, ProductInfo):
                    products.append(result)
                elif isinstance(result, dict):
                    products.append(ProductInfo(**result))

            if not products:
                raise Exception("Nessun dato disponibile")

            aggregated = AggregatedProductInfo.from_multiple_sources(products)

            return {
                "product": aggregated.dict(exclude={"_metadata", "_source_data"}),
                "debug": aggregated.get_debug_info()
            }

        except Exception as e:
            return {
                "error": str(e),
                "debug": {"error": str(e)}
            }