import pytest
from datetime import datetime
from app.api.core.markets import ProductInfo, Price


@pytest.mark.aggregator
@pytest.mark.market
class TestMarketDataAggregator:

    def __product(self, symbol: str, price: float, volume: float, currency: str, provider: str = "") -> ProductInfo:
        prod = ProductInfo()
        prod.id = f"{symbol}-{currency}"
        prod.symbol = symbol
        prod.price = price
        prod.volume_24h = volume
        prod.currency = currency
        prod.provider = provider
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
            "Provider1": [self.__product("BTC", 50000.0, 1000.0, "USD", "Provider1")],
            "Provider2": [self.__product("BTC", 50100.0, 1100.0, "USD", "Provider2")],
            "Provider3": [self.__product("BTC", 49900.0, 900.0, "USD", "Provider3")],
        }

        # aggregate_single_asset returns a single ProductInfo, not a list
        info = ProductInfo.aggregate_single_asset(products)
        assert info is not None
        assert info.symbol == "BTC"

        avg_weighted_price = (50000.0 * 1000.0 + 50100.0 * 1100.0 + 49900.0 * 900.0) / (1000.0 + 1100.0 + 900.0)
        assert info.price == pytest.approx(avg_weighted_price, rel=1e-3) # type: ignore
        assert info.volume_24h == pytest.approx(1000.0, rel=1e-3) # type: ignore
        assert info.currency == "USD"

    def test_aggregate_product_info_multiple_symbols(self):
        products = {
            "Provider1": [
                self.__product("BTC", 50000.0, 1000.0, "USD", "Provider1"),
                self.__product("ETH", 4000.0, 2000.0, "USD", "Provider1"),
            ],
            "Provider2": [
                self.__product("BTC", 50100.0, 1100.0, "USD", "Provider2"),
                self.__product("ETH", 4050.0, 2100.0, "USD", "Provider2"),
            ],
        }

        # aggregate_multi_assets aggregates by symbol across providers
        aggregated = ProductInfo.aggregate_multi_assets(products)
        assert len(aggregated) == 2

        btc_info = next((p for p in aggregated if p.symbol == "BTC"), None)
        eth_info = next((p for p in aggregated if p.symbol == "ETH"), None)

        assert btc_info is not None
        avg_weighted_price_btc = (50000.0 * 1000.0 + 50100.0 * 1100.0) / (1000.0 + 1100.0)
        assert btc_info.price == pytest.approx(avg_weighted_price_btc, rel=1e-3) # type: ignore
        assert btc_info.volume_24h == pytest.approx(2100.0, rel=1e-3) # type: ignore  # Total volume (1000 + 1100)
        assert btc_info.currency == "USD"

        assert eth_info is not None
        avg_weighted_price_eth = (4000.0 * 2000.0 + 4050.0 * 2100.0) / (2000.0 + 2100.0)
        assert eth_info.price == pytest.approx(avg_weighted_price_eth, rel=1e-3) # type: ignore
        assert eth_info.volume_24h == pytest.approx(4100.0, rel=1e-3) # type: ignore  # Total volume (2000 + 2100)
        assert eth_info.currency == "USD"

    def test_aggregate_product_info_with_no_data(self):
        products: dict[str, list[ProductInfo]] = {
            "Provider1": [],
            "Provider2": [],
        }
        aggregated = ProductInfo.aggregate_multi_assets(products)
        assert len(aggregated) == 0

    def test_aggregate_product_info_with_partial_data(self):
        products: dict[str, list[ProductInfo]] = {
            "Provider1": [self.__product("BTC", 50000.0, 1000.0, "USD", "Provider1")],
            "Provider2": [],
        }
        aggregated = ProductInfo.aggregate_multi_assets(products)
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
            "Provider1": [self.__product("BTC", 100000.0, 1000.0, "USD", "Provider1")],
            "Provider2": [self.__product("BTC", 70000.0, 800.0, "EUR", "Provider2")],
        }

        aggregated = ProductInfo.aggregate_multi_assets(products)
        assert len(aggregated) == 1

        info = aggregated[0]
        assert info is not None
        assert info.id == "BTC_AGGREGATED"
        assert info.symbol == "BTC"
        assert info.currency == "USD"  # Only USD products are kept
        # When currencies differ, only USD is aggregated (only Provider1 in this case)
        assert info.price == pytest.approx(100000.0, rel=1e-3) # type: ignore
        assert info.volume_24h == pytest.approx(1000.0, rel=1e-3) # type: ignore  # Only USD volume

    # ===== Tests for aggregate_single_asset =====

    def test_aggregate_single_asset_from_dict(self):
        """Test aggregate_single_asset with dict input (simulating WrapperHandler.try_call_all)"""
        products_dict: dict[str, ProductInfo] = {
            "BinanceWrapper": self.__product("BTC", 50000.0, 1000.0, "USD", "Binance"),
            "YFinanceWrapper": self.__product("BTC", 50100.0, 1100.0, "USD", "YFinance"),
            "CoinBaseWrapper": self.__product("BTC", 49900.0, 900.0, "USD", "Coinbase"),
        }

        info = ProductInfo.aggregate_single_asset(products_dict)
        assert info is not None
        assert info.symbol == "BTC"
        assert info.id == "BTC_AGGREGATED"
        assert "Binance" in info.provider
        assert "YFinance" in info.provider
        assert "Coinbase" in info.provider

        # VWAP calculation
        expected_price = (50000.0 * 1000.0 + 50100.0 * 1100.0 + 49900.0 * 900.0) / (1000.0 + 1100.0 + 900.0)
        assert info.price == pytest.approx(expected_price, rel=1e-3) # type: ignore
        assert info.volume_24h == pytest.approx(1000.0, rel=1e-3) # type: ignore
        assert info.currency == "USD"

    def test_aggregate_single_asset_from_list(self):
        """Test aggregate_single_asset with list input"""
        products_list = [
            self.__product("ETH", 4000.0, 2000.0, "USD", "Binance"),
            self.__product("ETH", 4050.0, 2100.0, "USD", "Coinbase"),
        ]

        info = ProductInfo.aggregate_single_asset(products_list)
        assert info is not None
        assert info.symbol == "ETH"
        assert info.id == "ETH_AGGREGATED"
        assert "Binance" in info.provider
        assert "Coinbase" in info.provider

        expected_price = (4000.0 * 2000.0 + 4050.0 * 2100.0) / (2000.0 + 2100.0)
        assert info.price == pytest.approx(expected_price, rel=1e-3) # type: ignore

    def test_aggregate_single_asset_no_volume_fallback(self):
        """Test fallback to simple average when no volume data"""
        products_list = [
            self.__product("SOL", 100.0, 0.0, "USD", "Provider1"),
            self.__product("SOL", 110.0, 0.0, "USD", "Provider2"),
            self.__product("SOL", 90.0, 0.0, "USD", "Provider3"),
        ]

        info = ProductInfo.aggregate_single_asset(products_list)
        assert info is not None
        assert info.symbol == "SOL"
        # Simple average: (100 + 110 + 90) / 3 = 100
        assert info.price == pytest.approx(100.0, rel=1e-3) # type: ignore
        assert info.volume_24h == pytest.approx(0.0, rel=1e-3) # type: ignore

    def test_aggregate_single_asset_empty_raises(self):
        """Test that empty input raises ValueError"""
        with pytest.raises(ValueError, match="requires at least one ProductInfo"):
            ProductInfo.aggregate_single_asset([])

        with pytest.raises(ValueError, match="requires at least one ProductInfo"):
            ProductInfo.aggregate_single_asset({})

    def test_aggregate_single_asset_dict_with_lists(self):
        """Test aggregate_single_asset with dict[str, list[ProductInfo]] (flattens correctly)"""
        products_dict_lists: dict[str, list[ProductInfo]] = {
            "Provider1": [self.__product("ADA", 0.50, 1000.0, "USD", "Provider1")],
            "Provider2": [self.__product("ADA", 0.52, 1200.0, "USD", "Provider2")],
        }

        info = ProductInfo.aggregate_single_asset(products_dict_lists)
        assert info is not None
        assert info.symbol == "ADA"
        expected_price = (0.50 * 1000.0 + 0.52 * 1200.0) / (1000.0 + 1200.0)
        assert info.price == pytest.approx(expected_price, rel=1e-3) # type: ignore

    def test_aggregate_single_asset_missing_currency(self):
        """Test that aggregate_single_asset handles missing currency gracefully"""
        products_list = [
            self.__product("DOT", 10.0, 500.0, "", "Provider1"),
            self.__product("DOT", 10.5, 600.0, "USD", "Provider2"),
        ]

        info = ProductInfo.aggregate_single_asset(products_list)
        assert info is not None
        assert info.symbol == "DOT"
        assert info.currency == "USD"  # Should pick the first non-empty currency

    def test_aggregate_single_asset_single_provider(self):
        """Test aggregate_single_asset with only one provider (edge case)"""
        products = {
            "BinanceWrapper": self.__product("MATIC", 0.80, 5000.0, "USD", "Binance"),
        }

        info = ProductInfo.aggregate_single_asset(products)
        assert info is not None
        assert info.symbol == "MATIC"
        assert info.price == pytest.approx(0.80, rel=1e-3) # type: ignore
        assert info.volume_24h == pytest.approx(5000.0, rel=1e-3) # type: ignore
        assert info.provider == "Binance"

    # ===== Tests for aggregate_multi_assets with edge cases =====

    def test_aggregate_multi_assets_empty_providers(self):
        """Test aggregate_multi_assets with some providers returning empty lists"""
        products = {
            "Provider1": [self.__product("BTC", 50000.0, 1000.0, "USD", "Provider1")],
            "Provider2": [],
            "Provider3": [self.__product("BTC", 50100.0, 1100.0, "USD", "Provider3")],
        }

        aggregated = ProductInfo.aggregate_multi_assets(products)
        assert len(aggregated) == 1
        info = aggregated[0]
        assert info.symbol == "BTC"
        assert "Provider1" in info.provider
        assert "Provider3" in info.provider

    def test_aggregate_multi_assets_mixed_symbols(self):
        """Test that aggregate_multi_assets correctly separates different symbols"""
        products = {
            "Provider1": [
                self.__product("BTC", 50000.0, 1000.0, "USD", "Provider1"),
                self.__product("ETH", 4000.0, 2000.0, "USD", "Provider1"),
                self.__product("SOL", 100.0, 500.0, "USD", "Provider1"),
            ],
            "Provider2": [
                self.__product("BTC", 50100.0, 1100.0, "USD", "Provider2"),
                self.__product("ETH", 4050.0, 2100.0, "USD", "Provider2"),
            ],
        }

        aggregated = ProductInfo.aggregate_multi_assets(products)
        assert len(aggregated) == 3

        symbols = {p.symbol for p in aggregated}
        assert symbols == {"BTC", "ETH", "SOL"}

        btc = next(p for p in aggregated if p.symbol == "BTC")
        assert "Provider1" in btc.provider and "Provider2" in btc.provider

        sol = next(p for p in aggregated if p.symbol == "SOL")
        assert sol.provider == "Provider1"  # Only one provider
