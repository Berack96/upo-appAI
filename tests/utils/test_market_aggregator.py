import pytest
from app.markets.base import ProductInfo, Price
from app.utils.market_aggregation import aggregate_history_prices, aggregate_product_info


@pytest.mark.aggregator
@pytest.mark.market
class TestMarketDataAggregator:

    def __product(self, symbol: str, price: float, volume: float, currency: str) -> ProductInfo:
        prod = ProductInfo()
        prod.id=f"{symbol}-{currency}"
        prod.symbol=symbol
        prod.price=price
        prod.volume_24h=volume
        prod.quote_currency=currency
        return prod

    def __price(self, timestamp_ms: int, high: float, low: float, open: float, close: float, volume: float) -> Price:
        price = Price()
        price.timestamp_ms = timestamp_ms
        price.high = high
        price.low = low
        price.open = open
        price.close = close
        price.volume = volume
        return price

    def test_aggregate_product_info(self):
        products: dict[str, list[ProductInfo]] = {
            "Provider1": [self.__product("BTC", 50000.0, 1000.0, "USD")],
            "Provider2": [self.__product("BTC", 50100.0, 1100.0, "USD")],
            "Provider3": [self.__product("BTC", 49900.0, 900.0, "USD")],
        }

        aggregated = aggregate_product_info(products)
        print(aggregated)
        assert len(aggregated) == 1

        info = aggregated[0]
        assert info is not None
        assert info.symbol == "BTC"
        assert info.price == pytest.approx(50000.0, rel=1e-3)

        avg_weighted_volume = (50000.0 * 1000.0 + 50100.0 * 1100.0 + 49900.0 * 900.0) / (1000.0 + 1100.0 + 900.0)
        assert info.volume_24h == pytest.approx(avg_weighted_volume, rel=1e-3)
        assert info.quote_currency == "USD"

    def test_aggregate_product_info_multiple_symbols(self):
        products = {
            "Provider1": [
                self.__product("BTC", 50000.0, 1000.0, "USD"),
                self.__product("ETH", 4000.0, 2000.0, "USD"),
            ],
            "Provider2": [
                self.__product("BTC", 50100.0, 1100.0, "USD"),
                self.__product("ETH", 4050.0, 2100.0, "USD"),
            ],
        }

        aggregated = aggregate_product_info(products)
        assert len(aggregated) == 2

        btc_info = next((p for p in aggregated if p.symbol == "BTC"), None)
        eth_info = next((p for p in aggregated if p.symbol == "ETH"), None)

        assert btc_info is not None
        assert btc_info.price == pytest.approx(50050.0, rel=1e-3)
        avg_weighted_volume_btc = (50000.0 * 1000.0 + 50100.0 * 1100.0) / (1000.0 + 1100.0)
        assert btc_info.volume_24h == pytest.approx(avg_weighted_volume_btc, rel=1e-3)
        assert btc_info.quote_currency == "USD"

        assert eth_info is not None
        assert eth_info.price == pytest.approx(4025.0, rel=1e-3)
        avg_weighted_volume_eth = (4000.0 * 2000.0 + 4050.0 * 2100.0) / (2000.0 + 2100.0)
        assert eth_info.volume_24h == pytest.approx(avg_weighted_volume_eth, rel=1e-3)
        assert eth_info.quote_currency == "USD"

    def test_aggregate_history_prices(self):
        """Test aggregazione di prezzi storici usando aggregate_history_prices"""

        prices = {
            "Provider1": [
                self.__price(1685577600000, 50000.0, 49500.0, 49600.0, 49900.0, 150.0),
                self.__price(1685581200000, 50200.0, 49800.0, 50000.0, 50100.0, 200.0),
            ],
            "Provider2": [
                self.__price(1685577600000, 50100.0, 49600.0, 49700.0, 50000.0, 180.0),
                self.__price(1685581200000, 50300.0, 49900.0, 50100.0, 50200.0, 220.0),
            ],
        }

        aggregated = aggregate_history_prices(prices)
        assert len(aggregated) == 2
        assert aggregated[0].timestamp_ms == 1685577600000
        assert aggregated[0].high == pytest.approx(50050.0, rel=1e-3)
        assert aggregated[0].low == pytest.approx(49500.0, rel=1e-3)
        assert aggregated[1].timestamp_ms == 1685581200000
        assert aggregated[1].high == pytest.approx(50250.0, rel=1e-3)
        assert aggregated[1].low == pytest.approx(49800.0, rel=1e-3)
