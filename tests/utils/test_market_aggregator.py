import pytest
from datetime import datetime
from app.api.core.markets import ProductInfo, Price


@pytest.mark.aggregator
@pytest.mark.market
class TestMarketDataAggregator:

    def __product(self, symbol: str, price: float, volume: float, currency: str) -> ProductInfo:
        prod = ProductInfo()
        prod.id=f"{symbol}-{currency}"
        prod.symbol=symbol
        prod.price=price
        prod.volume_24h=volume
        prod.currency=currency
        return prod

    def __price(self, timestamp_s: int, high: float, low: float, open: float, close: float, volume: float) -> Price:
        price = Price()
        price.set_timestamp(timestamp_s=timestamp_s)
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

        aggregated = ProductInfo.aggregate(products)
        assert len(aggregated) == 1

        info = aggregated[0]
        assert info is not None
        assert info.symbol == "BTC"

        avg_weighted_price = (50000.0 * 1000.0 + 50100.0 * 1100.0 + 49900.0 * 900.0) / (1000.0 + 1100.0 + 900.0)
        assert info.price == pytest.approx(avg_weighted_price, rel=1e-3) # type: ignore
        assert info.volume_24h == pytest.approx(1000.0, rel=1e-3) # type: ignore
        assert info.currency == "USD"

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

        aggregated = ProductInfo.aggregate(products)
        assert len(aggregated) == 2

        btc_info = next((p for p in aggregated if p.symbol == "BTC"), None)
        eth_info = next((p for p in aggregated if p.symbol == "ETH"), None)

        assert btc_info is not None
        avg_weighted_price_btc = (50000.0 * 1000.0 + 50100.0 * 1100.0) / (1000.0 + 1100.0)
        assert btc_info.price == pytest.approx(avg_weighted_price_btc, rel=1e-3) # type: ignore
        assert btc_info.volume_24h == pytest.approx(1050.0, rel=1e-3) # type: ignore
        assert btc_info.currency == "USD"

        assert eth_info is not None
        avg_weighted_price_eth = (4000.0 * 2000.0 + 4050.0 * 2100.0) / (2000.0 + 2100.0)
        assert eth_info.price == pytest.approx(avg_weighted_price_eth, rel=1e-3) # type: ignore
        assert eth_info.volume_24h == pytest.approx(2050.0, rel=1e-3) # type: ignore
        assert eth_info.currency == "USD"

    def test_aggregate_product_info_with_no_data(self):
        products: dict[str, list[ProductInfo]] = {
            "Provider1": [],
            "Provider2": [],
        }
        aggregated = ProductInfo.aggregate(products)
        assert len(aggregated) == 0

    def test_aggregate_product_info_with_partial_data(self):
        products: dict[str, list[ProductInfo]] = {
            "Provider1": [self.__product("BTC", 50000.0, 1000.0, "USD")],
            "Provider2": [],
        }
        aggregated = ProductInfo.aggregate(products)
        assert len(aggregated) == 1
        info = aggregated[0]
        assert info.symbol == "BTC"
        assert info.price == pytest.approx(50000.0, rel=1e-3) # type: ignore
        assert info.volume_24h == pytest.approx(1000.0, rel=1e-3) # type: ignore
        assert info.currency == "USD"

    def test_aggregate_history_prices(self):
        """Test aggregazione di prezzi storici usando aggregate_history_prices"""
        timestamp_now = datetime.now()
        timestamp_1h_ago = int(timestamp_now.replace(hour=timestamp_now.hour - 1).timestamp())
        timestamp_2h_ago = int(timestamp_now.replace(hour=timestamp_now.hour - 2).timestamp())

        prices = {
            "Provider1": [
                self.__price(timestamp_1h_ago, 50000.0, 49500.0, 49600.0, 49900.0, 150.0),
                self.__price(timestamp_2h_ago, 50200.0, 49800.0, 50000.0, 50100.0, 200.0),
            ],
            "Provider2": [
                self.__price(timestamp_1h_ago, 50100.0, 49600.0, 49700.0, 50000.0, 180.0),
                self.__price(timestamp_2h_ago, 50300.0, 49900.0, 50100.0, 50200.0, 220.0),
            ],
        }

        price = Price()
        price.set_timestamp(timestamp_s=timestamp_1h_ago)
        timestamp_1h_ago = price.timestamp
        price.set_timestamp(timestamp_s=timestamp_2h_ago)
        timestamp_2h_ago = price.timestamp

        aggregated = Price.aggregate(prices)
        assert len(aggregated) == 2
        assert aggregated[0].timestamp == timestamp_1h_ago
        assert aggregated[0].high == pytest.approx(50050.0, rel=1e-3) # type: ignore
        assert aggregated[0].low == pytest.approx(49550.0, rel=1e-3) # type: ignore
        assert aggregated[1].timestamp == timestamp_2h_ago
        assert aggregated[1].high == pytest.approx(50250.0, rel=1e-3) # type: ignore
        assert aggregated[1].low == pytest.approx(49850.0, rel=1e-3) # type: ignore

    def test_aggregate_product_info_different_currencies(self):
        products: dict[str, list[ProductInfo]] = {
            "Provider1": [self.__product("BTC", 100000.0, 1000.0, "USD")],
            "Provider2": [self.__product("BTC", 70000.0, 800.0, "EUR")],
        }

        aggregated = ProductInfo.aggregate(products)
        assert len(aggregated) == 1

        info = aggregated[0]
        assert info is not None
        assert info.id == "BTC-USD_AGGREGATED"
        assert info.symbol == "BTC"
        assert info.currency == "USD"
        assert info.price == pytest.approx(100000.0, rel=1e-3) # type: ignore
        assert info.volume_24h == pytest.approx(1000.0, rel=1e-3) # type: ignore

        info = aggregated[1]
        assert info is not None
        assert info.id == "BTC-EUR_AGGREGATED"
        assert info.symbol == "BTC"
        assert info.currency == "EUR"
        assert info.price == pytest.approx(70000.0, rel=1e-3) # type: ignore
        assert info.volume_24h == pytest.approx(800.0, rel=1e-3) # type: ignore
