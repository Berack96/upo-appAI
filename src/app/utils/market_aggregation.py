import statistics
from app.markets.base import ProductInfo, Price


def aggregate_history_prices(prices: dict[str, list[Price]]) -> list[float]:
    """Aggrega i prezzi storici per symbol calcolando la media"""
    raise NotImplementedError("Funzione non ancora implementata per problemi di timestamp he deve essere uniformato prima di usare questa funzione.")
    # TODO implementare l'aggregazione dopo aver modificato la classe Price in modo che abbia un timestamp integer
    # aggregated_prices = []
    # for timestamp in range(len(next(iter(prices.values())))):
    #     timestamp_prices = [
    #         price_list[timestamp].price
    #         for price_list in prices.values()
    #         if len(price_list) > timestamp and price_list[timestamp].price is not None
    #     ]
    #     if timestamp_prices:
    #         aggregated_prices.append(statistics.mean(timestamp_prices))
    #     else:
    #         aggregated_prices.append(None)
    # return aggregated_prices

def aggregate_product_info(products: dict[str, list[ProductInfo]]) -> list[ProductInfo]:
    """
    Aggrega una lista di ProductInfo per symbol.
    """

    # Costruzione mappa symbol -> lista di ProductInfo
    symbols_infos: dict[str, list[ProductInfo]] = {}
    for _, product_list in products.items():
        for product in product_list:
            symbols_infos.setdefault(product.symbol, []).append(product)

    # Aggregazione per ogni symbol
    sources = list(products.keys())
    aggregated_products = []
    for symbol, product_list in symbols_infos.items():
        product = ProductInfo()

        product.id = f"{symbol}_AGG"
        product.symbol = symbol
        product.quote_currency = next(p.quote_currency for p in product_list if p.quote_currency)

        statuses = {}
        for p in product_list:
            statuses[p.status] = statuses.get(p.status, 0) + 1
        product.status = max(statuses, key=statuses.get) if statuses else ""

        prices = [p.price for p in product_list]
        product.price = statistics.mean(prices)

        volumes = [p.volume_24h for p in product_list]
        product.volume_24h = sum([p * v for p, v in zip(prices, volumes)]) / sum(volumes)
        aggregated_products.append(product)

        confidence = _calculate_confidence(product_list, sources) # TODO necessary?

    return aggregated_products

def _calculate_confidence(products: list[ProductInfo], sources: list[str]) -> float:
    """Calcola un punteggio di confidenza 0-1"""
    if not products:
        return 0.0

    score = 1.0

    # Riduci score se pochi dati
    if len(products) < 2:
        score *= 0.7

    # Riduci score se prezzi troppo diversi
    prices = [p.price for p in products if p.price > 0]
    if len(prices) > 1:
        price_std = (max(prices) - min(prices)) / statistics.mean(prices)
        if price_std > 0.05:  # >5% variazione
            score *= 0.8

    # Riduci score se fonti sconosciute
    unknown_sources = sum(1 for s in sources if s == "unknown")
    if unknown_sources > 0:
        score *= (1 - unknown_sources / len(sources))

    return max(0.0, min(1.0, score))
