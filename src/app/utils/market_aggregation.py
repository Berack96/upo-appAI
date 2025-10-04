import statistics
from app.markets.base import ProductInfo, Price


def aggregate_history_prices(prices: dict[str, list[Price]]) -> list[Price]:
    """
    Aggrega i prezzi storici per symbol calcolando la media oraria.
    Args:
        prices (dict[str, list[Price]]): Mappa provider -> lista di Price
    Returns:
        list[Price]: Lista di Price aggregati per ora
    """

    # Costruiamo una mappa timestamp_h -> lista di Price
    timestamped_prices: dict[int, list[Price]] = {}
    for _, price_list in prices.items():
        for price in price_list:
            time = price.timestamp_ms - (price.timestamp_ms % 3600000)  # arrotonda all'ora (non dovrebbe essere necessario)
            timestamped_prices.setdefault(time, []).append(price)

    # Ora aggregiamo i prezzi per ogni ora
    aggregated_prices: list[Price] = []
    for time, price_list in timestamped_prices.items():
        price = Price()
        price.timestamp_ms = time
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
        product.quote_currency = next(p.quote_currency for p in product_list if p.quote_currency)

        volume_sum = sum(p.volume_24h for p in product_list)
        product.volume_24h = volume_sum / len(product_list) if product_list else 0.0

        prices = sum(p.price * p.volume_24h for p in product_list)
        product.price = (prices / volume_sum) if volume_sum > 0 else 0.0

        aggregated_products.append(product)
    return aggregated_products

