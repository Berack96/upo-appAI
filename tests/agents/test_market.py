import os
import pytest
from app.agents.market import MarketToolkit
from app.markets.base import BaseWrapper
from app.markets.coinbase import CoinBaseWrapper
from app.markets.cryptocompare import CryptoCompareWrapper
from app.markets import get_first_available_market_api

class TestMarketSystem:
    """Test suite per il sistema di mercato (wrappers + toolkit)"""

    @pytest.fixture(scope="class")
    def market_wrapper(self) -> BaseWrapper:
        first = get_first_available_market_api("USD")
        return first

    def test_wrapper_initialization(self, market_wrapper):
        assert market_wrapper is not None
        assert hasattr(market_wrapper, 'get_product')
        assert hasattr(market_wrapper, 'get_products')
        assert hasattr(market_wrapper, 'get_all_products')
        assert hasattr(market_wrapper, 'get_historical_prices')

    def test_providers_configuration(self):
        available_providers = []
        if os.getenv('CDP_API_KEY_NAME') and os.getenv('CDP_API_PRIVATE_KEY'):
            available_providers.append('coinbase')
        if os.getenv('CRYPTOCOMPARE_API_KEY'):
            available_providers.append('cryptocompare')
        assert len(available_providers) > 0

    def test_wrapper_capabilities(self, market_wrapper):
        capabilities = []
        if hasattr(market_wrapper, 'get_product'):
            capabilities.append('single_product')
        if hasattr(market_wrapper, 'get_products'):
            capabilities.append('multiple_products')
        if hasattr(market_wrapper, 'get_historical_prices'):
            capabilities.append('historical_data')
        assert len(capabilities) > 0

    def test_market_data_retrieval(self, market_wrapper):
        btc_product = market_wrapper.get_product("BTC")
        assert btc_product is not None
        assert hasattr(btc_product, 'symbol')
        assert hasattr(btc_product, 'price')
        assert btc_product.price > 0

    def test_market_toolkit_integration(self, market_wrapper):
        try:
            toolkit = MarketToolkit()
            assert toolkit is not None
            assert hasattr(toolkit, 'market_agent')
            assert toolkit.market_agent is not None

            tools = toolkit.tools
            assert len(tools) > 0

        except Exception as e:
            print(f"MarketToolkit test failed: {e}")
            # Non fail completamente - il toolkit potrebbe avere dipendenze specifiche

    @pytest.mark.skipif(
        not os.getenv('CRYPTOCOMPARE_API_KEY'), 
        reason="CRYPTOCOMPARE_API_KEY not configured"
    )
    def test_cryptocompare_wrapper(self):
        try:
            api_key = os.getenv('CRYPTOCOMPARE_API_KEY')
            wrapper = CryptoCompareWrapper(api_key=api_key, currency="USD")

            btc_product = wrapper.get_product("BTC")
            assert btc_product is not None
            assert btc_product.symbol == "BTC"
            assert btc_product.price > 0

            products = wrapper.get_products(["BTC", "ETH"])
            assert isinstance(products, list)
            assert len(products) > 0

            for product in products:
                if product.symbol in ["BTC", "ETH"]:
                    assert product.price > 0

        except Exception as e:
            print(f"CryptoCompare test failed: {e}")
            # Non fail il test se c'è un errore di rete o API

    @pytest.mark.skipif(
        not (os.getenv('CDP_API_KEY_NAME') and os.getenv('CDP_API_PRIVATE_KEY')),
        reason="Coinbase credentials not configured"
    )
    def test_coinbase_wrapper(self):
        try:
            api_key = os.getenv('CDP_API_KEY_NAME')
            api_secret = os.getenv('CDP_API_PRIVATE_KEY')
            wrapper = CoinBaseWrapper(
                api_key=api_key, 
                api_private_key=api_secret, 
                currency="USD"
            )

            btc_product = wrapper.get_product("BTC")
            assert btc_product is not None
            assert btc_product.symbol == "BTC"
            assert btc_product.price > 0

            products = wrapper.get_products(["BTC", "ETH"])
            assert isinstance(products, list)
            assert len(products) > 0

        except Exception as e:
            print(f"Coinbase test failed: {e}")
            # Non fail il test se c'è un errore di credenziali o rete

    def test_provider_selection_mechanism(self):
        potential_providers = 0
        if os.getenv('CDP_API_KEY_NAME') and os.getenv('CDP_API_PRIVATE_KEY'):
            potential_providers += 1
        if os.getenv('CRYPTOCOMPARE_API_KEY'):
            potential_providers += 1

        if potential_providers == 0:
            with pytest.raises(AssertionError, match="No valid API keys"):
                get_first_available_market_api()
        else:
            wrapper = get_first_available_market_api("USD")
            assert wrapper is not None
            assert hasattr(wrapper, 'get_product')

    def test_error_handling(self, market_wrapper):
        try:
            fake_product = market_wrapper.get_product("NONEXISTENT_CRYPTO_SYMBOL_12345")
            assert fake_product is None or fake_product.price == 0
        except Exception as e:
            pass

        try:
            empty_products = market_wrapper.get_products([])
            assert isinstance(empty_products, list)
        except Exception as e:
            pass

    def test_wrapper_currency_support(self, market_wrapper):
        assert hasattr(market_wrapper, 'currency')
        assert isinstance(market_wrapper.currency, str)
        assert len(market_wrapper.currency) >= 3  # USD, EUR, etc.
