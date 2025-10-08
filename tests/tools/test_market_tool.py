import pytest
from app.markets import MarketAPIsTool


@pytest.mark.tools
@pytest.mark.market
@pytest.mark.api
class TestMarketAPIsTool:
    def test_wrapper_initialization(self):
        market_wrapper = MarketAPIsTool("EUR")
        assert market_wrapper is not None
        assert hasattr(market_wrapper, 'get_product')
        assert hasattr(market_wrapper, 'get_products')
        assert hasattr(market_wrapper, 'get_historical_prices')

    def test_wrapper_capabilities(self):
        market_wrapper = MarketAPIsTool("EUR")
        capabilities: list[str] = []
        if hasattr(market_wrapper, 'get_product'):
            capabilities.append('single_product')
        if hasattr(market_wrapper, 'get_products'):
            capabilities.append('multiple_products')
        if hasattr(market_wrapper, 'get_historical_prices'):
            capabilities.append('historical_data')
        assert len(capabilities) > 0

    def test_market_data_retrieval(self):
        market_wrapper = MarketAPIsTool("EUR")
        btc_product = market_wrapper.get_product("BTC")
        assert btc_product is not None
        assert hasattr(btc_product, 'symbol')
        assert hasattr(btc_product, 'price')
        assert btc_product.price > 0

    def test_error_handling(self):
        try:
            market_wrapper = MarketAPIsTool("EUR")
            fake_product = market_wrapper.get_product("NONEXISTENT_CRYPTO_SYMBOL_12345")
            assert fake_product is None or fake_product.price == 0
        except Exception as _:
            pass
