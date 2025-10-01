import pytest
from app.markets import YFinanceWrapper

@pytest.mark.market
@pytest.mark.api
class TestYFinance:

    def test_yfinance_init(self):
        market = YFinanceWrapper()
        assert market is not None
        assert hasattr(market, 'currency')
        assert market.currency == "USD"
        assert hasattr(market, 'tool')
        assert market.tool is not None

    def test_yfinance_get_crypto_product(self):
        market = YFinanceWrapper()
        product = market.get_product("BTC")
        assert product is not None
        assert hasattr(product, 'symbol')
        # BTC verrà convertito in BTC-USD dal formattatore
        assert product.symbol in ["BTC", "BTC-USD"]
        assert hasattr(product, 'price')
        assert product.price > 0

    def test_yfinance_get_products(self):
        market = YFinanceWrapper()
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

    def test_yfinance_invalid_product(self):
        market = YFinanceWrapper()
        with pytest.raises(Exception):
            _ = market.get_product("INVALIDSYMBOL123")

    def test_yfinance_crypto_history(self):
        market = YFinanceWrapper()
        history = market.get_historical_prices("BTC", limit=3)
        assert history is not None
        assert isinstance(history, list)
        assert len(history) == 3
        for entry in history:
            assert hasattr(entry, 'time')
            assert hasattr(entry, 'close')
            assert entry.close > 0
            assert hasattr(entry, 'open')
            assert entry.open > 0