import pytest
from app.api.tools import CryptoSymbolsTools

@pytest.mark.tools
class TestCryptoSymbolsTools:

    def test_get_symbols(self):
        tool = CryptoSymbolsTools()
        symbols = tool.get_all_symbols()
        assert isinstance(symbols, list)
        assert "BTC-USD" in symbols

    def test_get_symbol_by_name(self):
        tool = CryptoSymbolsTools()
        results = tool.get_symbols_by_name("Bitcoin")
        assert isinstance(results, list)
        assert ("BTC-USD", "Bitcoin USD") in results

        results = tool.get_symbols_by_name("Banana")
        assert isinstance(results, list)
        assert ("BANANA28886-USD", "BananaCoin USD") in results

    def test_get_symbol_by_invalid_name(self):
        tool = CryptoSymbolsTools()
        results = tool.get_symbols_by_name("InvalidName")
        assert isinstance(results, list)
        assert not results
