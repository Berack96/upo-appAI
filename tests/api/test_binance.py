import pytest
from app.markets.binance import BinanceWrapper

@pytest.mark.market
@pytest.mark.api
class TestBinance:

    def test_binance_init(self):
        market = BinanceWrapper()
        assert market is not None
        assert hasattr(market, 'currency')
        assert market.currency == "USDT"

    def test_binance_get_product(self):
        market = BinanceWrapper()
        product = market.get_product("BTC")
        assert product is not None
        assert hasattr(product, 'symbol')
        assert product.symbol == "BTC"
        assert hasattr(product, 'price')
        assert product.price > 0

    def test_binance_get_products(self):
        market = BinanceWrapper()
        products = market.get_products(["BTC", "ETH"])
        assert products is not None
        assert isinstance(products, list)
        assert len(products) == 2
        symbols = [p.symbol for p in products]
        assert "BTC" in symbols
        assert "ETH" in symbols
        for product in products:
            assert hasattr(product, 'price')
            assert product.price > 0

    def test_binance_invalid_product(self):
        market = BinanceWrapper()
        with pytest.raises(Exception):
            _ = market.get_product("INVALID")

    def test_binance_history(self):
        market = BinanceWrapper()
        history = market.get_historical_prices("BTC", limit=5)
        assert history is not None
        assert isinstance(history, list)
        assert len(history) == 5
        for entry in history:
            assert hasattr(entry, 'timestamp_ms')
            assert hasattr(entry, 'close')
            assert hasattr(entry, 'high')
            assert entry.close > 0
            assert entry.high > 0
            assert entry.timestamp_ms > 0
