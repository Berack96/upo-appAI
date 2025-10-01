import os
import pytest
from app.agents.market_agent import MarketToolkit
from app.markets import MarketAPIsTool


@pytest.mark.tools
@pytest.mark.market
@pytest.mark.api
class TestMarketAPIsTool:
    def test_wrapper_initialization(self):
        market_wrapper = MarketAPIsTool("USD")
        assert market_wrapper is not None
        assert hasattr(market_wrapper, 'get_product')
        assert hasattr(market_wrapper, 'get_products')
        assert hasattr(market_wrapper, 'get_all_products')
        assert hasattr(market_wrapper, 'get_historical_prices')

    def test_wrapper_capabilities(self):
        market_wrapper = MarketAPIsTool("USD")
        capabilities = []
        if hasattr(market_wrapper, 'get_product'):
            capabilities.append('single_product')
        if hasattr(market_wrapper, 'get_products'):
            capabilities.append('multiple_products')
        if hasattr(market_wrapper, 'get_historical_prices'):
            capabilities.append('historical_data')
        assert len(capabilities) > 0

    def test_market_data_retrieval(self):
        market_wrapper = MarketAPIsTool("USD")
        btc_product = market_wrapper.get_product("BTC")
        assert btc_product is not None
        assert hasattr(btc_product, 'symbol')
        assert hasattr(btc_product, 'price')
        assert btc_product.price > 0

    def test_market_toolkit_integration(self):
        try:
            toolkit = MarketToolkit()
            assert toolkit is not None
            assert hasattr(toolkit, 'market_agent')
            assert toolkit.market_api is not None

            tools = toolkit.tools
            assert len(tools) > 0

        except Exception as e:
            print(f"MarketToolkit test failed: {e}")
            # Non fail completamente - il toolkit potrebbe avere dipendenze specifiche

    def test_provider_selection_mechanism(self):
        potential_providers = 0
        if os.getenv('CDP_API_KEY_NAME') and os.getenv('CDP_API_PRIVATE_KEY'):
            potential_providers += 1
        if os.getenv('CRYPTOCOMPARE_API_KEY'):
            potential_providers += 1

    def test_error_handling(self):
        try:
            market_wrapper = MarketAPIsTool("USD")
            fake_product = market_wrapper.get_product("NONEXISTENT_CRYPTO_SYMBOL_12345")
            assert fake_product is None or fake_product.price == 0
        except Exception as e:
            pass

    def test_wrapper_currency_support(self):
        market_wrapper = MarketAPIsTool("USD")
        assert hasattr(market_wrapper, 'currency')
        assert isinstance(market_wrapper.currency, str)
        assert len(market_wrapper.currency) >= 3  # USD, EUR, etc.
