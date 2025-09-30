import os
import pytest
from app.markets import CoinBaseWrapper

@pytest.mark.market
@pytest.mark.api
@pytest.mark.skipif(not(os.getenv('COINBASE_API_KEY')) or not(os.getenv('COINBASE_API_SECRET')), reason="COINBASE_API_KEY or COINBASE_API_SECRET not set in environment variables")
class TestCoinBase:

    def test_coinbase_init(self):
        market = CoinBaseWrapper()
        assert market is not None
        assert hasattr(market, 'currency')
        assert market.currency == "USD"

    def test_coinbase_get_product(self):
        market = CoinBaseWrapper()
        product = market.get_product("BTC")
        assert product is not None
        assert hasattr(product, 'symbol')
        assert product.symbol == "BTC"
        assert hasattr(product, 'price')
        assert product.price > 0

    def test_coinbase_get_products(self):
        market = CoinBaseWrapper()
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

    def test_coinbase_invalid_product(self):
        market = CoinBaseWrapper()
        with pytest.raises(Exception):
            _ = market.get_product("INVALID")

    def test_coinbase_history(self):
        market = CoinBaseWrapper()
        history = market.get_historical_prices("BTC", limit=5)
        assert history is not None
        assert isinstance(history, list)
        assert len(history) == 5
        for entry in history:
            assert hasattr(entry, 'time')
            assert hasattr(entry, 'close')
            assert hasattr(entry, 'high')
            assert entry.close > 0
            assert entry.high > 0
