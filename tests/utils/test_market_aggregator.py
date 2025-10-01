import pytest
from app.markets.base import ProductInfo, Price
from app.utils.market_aggregation import aggregate_history_prices, aggregate_product_info


@pytest.mark.aggregator
@pytest.mark.market
class TestMarketDataAggregator:

    def __product(self, symbol: str, price: float, volume: float, status: str, currency: str) -> ProductInfo:
        prod = ProductInfo()
        prod.id=f"{symbol}-{currency}"
        prod.symbol=symbol
        prod.price=price
        prod.volume_24h=volume
        prod.status=status
        prod.quote_currency=currency
        return prod

    def test_aggregate_product_info(self):
        products: dict[str, list[ProductInfo]] = {
            "Provider1": [self.__product("BTC", 50000.0, 1000.0, "active", "USD")],
            "Provider2": [self.__product("BTC", 50100.0, 1100.0, "active", "USD")],
            "Provider3": [self.__product("BTC", 49900.0, 900.0, "inactive", "USD")],
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
        assert info.status == "active"
        assert info.quote_currency == "USD"

    def test_aggregate_product_info_multiple_symbols(self):
        products = {
            "Provider1": [
                self.__product("BTC", 50000.0, 1000.0, "active", "USD"),
                self.__product("ETH", 4000.0, 2000.0, "active", "USD"),
            ],
            "Provider2": [
                self.__product("BTC", 50100.0, 1100.0, "active", "USD"),
                self.__product("ETH", 4050.0, 2100.0, "active", "USD"),
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
        assert btc_info.status == "active"
        assert btc_info.quote_currency == "USD"

        assert eth_info is not None
        assert eth_info.price == pytest.approx(4025.0, rel=1e-3)
        avg_weighted_volume_eth = (4000.0 * 2000.0 + 4050.0 * 2100.0) / (2000.0 + 2100.0)
        assert eth_info.volume_24h == pytest.approx(avg_weighted_volume_eth, rel=1e-3)
        assert eth_info.status == "active"
        assert eth_info.quote_currency == "USD"

    def test_aggregate_history_prices(self):
        """Test aggregazione di prezzi storici usando aggregate_history_prices"""

        price1 = Price(
            timestamp="2024-06-01T00:00:00Z",
            price=50000.0,
            source="exchange1"
        )
        price2 = Price(
            timestamp="2024-06-01T00:00:00Z",
            price=50100.0,
            source="exchange2"
        )
        price3 = Price(
            timestamp="2024-06-01T01:00:00Z",
            price=50200.0,
            source="exchange1"
        )
        price4 = Price(
            timestamp="2024-06-01T01:00:00Z",
            price=50300.0,
            source="exchange2"
        )

        prices = [price1, price2, price3, price4]
        aggregated_prices = aggregate_history_prices(prices)

        assert len(aggregated_prices) == 2
        assert aggregated_prices[0].timestamp == "2024-06-01T00:00:00Z"
        assert aggregated_prices[0].price == pytest.approx(50050.0, rel=1e-3)
        assert aggregated_prices[1].timestamp == "2024-06-01T01:00:00Z"
        assert aggregated_prices[1].price == pytest.approx(50250.0, rel=1e-3)
