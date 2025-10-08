import os
import pytest
from app.markets import CryptoCompareWrapper

@pytest.mark.market
@pytest.mark.api
@pytest.mark.skipif(not os.getenv('CRYPTOCOMPARE_API_KEY'), reason="CRYPTOCOMPARE_API_KEY not set in environment variables")
class TestCryptoCompare:

    def test_cryptocompare_init(self):
        market = CryptoCompareWrapper()
        assert market is not None
        assert hasattr(market, 'api_key')
        assert market.api_key == os.getenv('CRYPTOCOMPARE_API_KEY')
        assert hasattr(market, 'currency')
        assert market.currency == "USD"

    def test_cryptocompare_get_product(self):
        market = CryptoCompareWrapper()
        product = market.get_product("BTC")
        assert product is not None
        assert hasattr(product, 'symbol')
        assert product.symbol == "BTC"
        assert hasattr(product, 'price')
        assert product.price > 0

    def test_cryptocompare_get_products(self):
        market = CryptoCompareWrapper()
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

    def test_cryptocompare_invalid_product(self):
        market = CryptoCompareWrapper()
        with pytest.raises(Exception):
            _ = market.get_product("INVALID")

    def test_cryptocompare_history(self):
        market = CryptoCompareWrapper()
        history = market.get_historical_prices("BTC", limit=5)
        assert history is not None
        assert isinstance(history, list)
        assert len(history) == 5
        for entry in history:
            assert hasattr(entry, 'timestamp')
            assert hasattr(entry, 'close')
            assert hasattr(entry, 'high')
            assert entry.close > 0
            assert entry.high > 0
            assert entry.timestamp != ''
