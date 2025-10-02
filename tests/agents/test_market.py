"""
Test suite completo per il sistema di mercato.

Questo modulo testa approfonditamente tutte le implementazioni di BaseWrapper
e verifica la conformità all'interfaccia definita in base.py.
"""

import os
from unittest.mock import Mock, patch

import pytest

from app.markets import MarketAPIs
# Import delle classi da testare
from app.markets.base import BaseWrapper, ProductInfo, Price
from app.markets.binance import BinanceWrapper
from app.markets.binance_public import PublicBinanceAgent
from app.markets.coinbase import CoinBaseWrapper
from app.markets.cryptocompare import CryptoCompareWrapper


class TestBaseWrapperInterface:
    """Test per verificare che tutte le implementazioni rispettino l'interfaccia BaseWrapper."""
    
    def test_all_wrappers_extend_basewrapper(self):
        """Verifica che tutte le classi wrapper estendano BaseWrapper."""
        wrapper_classes = [
            CoinBaseWrapper,
            CryptoCompareWrapper, 
            BinanceWrapper,
            PublicBinanceAgent,
            MarketAPIs
        ]
        
        for wrapper_class in wrapper_classes:
            assert issubclass(wrapper_class, BaseWrapper), f"{wrapper_class.__name__} deve estendere BaseWrapper"
    
    def test_all_wrappers_implement_required_methods(self):
        """Verifica che tutte le classi implementino i metodi richiesti dall'interfaccia."""
        wrapper_classes = [
            CoinBaseWrapper,
            CryptoCompareWrapper,
            BinanceWrapper,
            PublicBinanceAgent,
            MarketAPIs
        ]
        
        required_methods = ['get_product', 'get_products', 'get_all_products', 'get_historical_prices']
        
        for wrapper_class in wrapper_classes:
            for method in required_methods:
                assert hasattr(wrapper_class, method), f"{wrapper_class.__name__} deve implementare {method}"
                assert callable(getattr(wrapper_class, method)), f"{method} deve essere callable in {wrapper_class.__name__}"


class TestProductInfoModel:
    """Test per la classe ProductInfo e i suoi metodi di conversione."""
    
    def test_productinfo_initialization(self):
        """Test inizializzazione di ProductInfo."""
        product = ProductInfo()
        assert product.id == ""
        assert product.symbol == ""
        assert product.price == 0.0
        assert product.volume_24h == 0.0
        assert product.status == ""
        assert product.quote_currency == ""
    
    def test_productinfo_with_data(self):
        """Test ProductInfo con dati specifici."""
        product = ProductInfo(
            id="BTC-USD",
            symbol="BTC",
            price=50000.0,
            volume_24h=1000000.0,
            status="TRADING",
            quote_currency="USD"
        )
        assert product.id == "BTC-USD"
        assert product.symbol == "BTC"
        assert product.price == 50000.0
        assert product.volume_24h == 1000000.0
        assert product.status == "TRADING"
        assert product.quote_currency == "USD"
    
    def test_productinfo_from_cryptocompare(self):
        """Test conversione da dati CryptoCompare."""
        mock_data = {
            'FROMSYMBOL': 'BTC',
            'TOSYMBOL': 'USD',
            'PRICE': 50000.0,
            'VOLUME24HOUR': 1000000.0
        }
        
        product = ProductInfo.from_cryptocompare(mock_data)
        assert product.id == "BTC-USD"
        assert product.symbol == "BTC"
        assert product.price == 50000.0
        assert product.volume_24h == 1000000.0
        assert product.status == ""
    
    def test_productinfo_from_binance(self):
        """Test conversione da dati Binance."""
        ticker_data = {'symbol': 'BTCUSDT', 'price': '50000.0'}
        ticker_24h_data = {'volume': '1000000.0'}
        
        product = ProductInfo.from_binance(ticker_data, ticker_24h_data)
        assert product.id == "BTCUSDT"
        assert product.symbol == "BTC"
        assert product.price == 50000.0
        assert product.volume_24h == 1000000.0
        assert product.status == "TRADING"
        assert product.quote_currency == "USDT"


class TestPriceModel:
    """Test per la classe Price e i suoi metodi di conversione."""
    
    def test_price_initialization(self):
        """Test inizializzazione di Price."""
        price = Price()
        assert price.high == 0.0
        assert price.low == 0.0
        assert price.open == 0.0
        assert price.close == 0.0
        assert price.volume == 0.0
        assert price.time == ""
    
    def test_price_with_data(self):
        """Test Price con dati specifici."""
        price = Price(
            high=51000.0,
            low=49000.0,
            open=50000.0,
            close=50500.0,
            volume=1000.0,
            time="2024-01-01T00:00:00Z"
        )
        assert price.high == 51000.0
        assert price.low == 49000.0
        assert price.open == 50000.0
        assert price.close == 50500.0
        assert price.volume == 1000.0
        assert price.time == "2024-01-01T00:00:00Z"
    
    def test_price_from_cryptocompare(self):
        """Test conversione da dati CryptoCompare."""
        mock_data = {
            'high': 51000.0,
            'low': 49000.0,
            'open': 50000.0,
            'close': 50500.0,
            'volumeto': 1000.0,
            'time': 1704067200
        }
        
        price = Price.from_cryptocompare(mock_data)
        assert price.high == 51000.0
        assert price.low == 49000.0
        assert price.open == 50000.0
        assert price.close == 50500.0
        assert price.volume == 1000.0
        assert price.time == "1704067200"


class TestCoinBaseWrapper:
    """Test specifici per CoinBaseWrapper."""
    
    @pytest.mark.skipif(
        not (os.getenv('COINBASE_API_KEY') and os.getenv('COINBASE_API_SECRET')),
        reason="Credenziali Coinbase non configurate"
    )
    def test_coinbase_initialization_with_env_vars(self):
        """Test inizializzazione con variabili d'ambiente."""
        wrapper = CoinBaseWrapper(currency="USD")
        assert wrapper.currency == "USD"
        assert wrapper.client is not None
    
    @patch.dict(os.environ, {}, clear=True)
    def test_coinbase_initialization_with_params(self):
        """Test inizializzazione con parametri espliciti quando non ci sono variabili d'ambiente."""
        with pytest.raises(AssertionError, match="API key is required"):
            CoinBaseWrapper(api_key=None, api_private_key=None)
    
    @patch('app.markets.coinbase.RESTClient')
    def test_coinbase_asset_formatting_behavior(self, mock_client):
        """Test comportamento di formattazione asset ID attraverso get_product."""
        mock_response = Mock()
        mock_response.product_id = "BTC-USD"
        mock_response.base_currency_id = "BTC"
        mock_response.price = "50000.0"
        mock_response.volume_24h = "1000000.0"
        mock_response.status = "TRADING"
        
        mock_client_instance = Mock()
        mock_client_instance.get_product.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        wrapper = CoinBaseWrapper(api_key="test", api_private_key="test")
        
        # Test che entrambi i formati funzionino
        wrapper.get_product("BTC")
        wrapper.get_product("BTC-USD")
        
        # Verifica che get_product sia stato chiamato con il formato corretto
        assert mock_client_instance.get_product.call_count == 2
    
    @patch('app.markets.coinbase.RESTClient')
    def test_coinbase_get_product(self, mock_client):
        """Test get_product con mock."""
        mock_response = Mock()
        mock_response.product_id = "BTC-USD"
        mock_response.base_currency_id = "BTC"
        mock_response.price = "50000.0"
        mock_response.volume_24h = "1000000.0"
        mock_response.status = "TRADING"
        
        mock_client_instance = Mock()
        mock_client_instance.get_product.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        wrapper = CoinBaseWrapper(api_key="test", api_private_key="test")
        product = wrapper.get_product("BTC")
        
        assert isinstance(product, ProductInfo)
        assert product.symbol == "BTC"
        mock_client_instance.get_product.assert_called_once_with("BTC-USD")


class TestCryptoCompareWrapper:
    """Test specifici per CryptoCompareWrapper."""
    
    @pytest.mark.skipif(
        not os.getenv('CRYPTOCOMPARE_API_KEY'),
        reason="CRYPTOCOMPARE_API_KEY non configurata"
    )
    def test_cryptocompare_initialization_with_env_var(self):
        """Test inizializzazione con variabile d'ambiente."""
        wrapper = CryptoCompareWrapper(currency="USD")
        assert wrapper.currency == "USD"
        assert wrapper.api_key is not None
    
    def test_cryptocompare_initialization_with_param(self):
        """Test inizializzazione con parametro esplicito."""
        wrapper = CryptoCompareWrapper(api_key="test_key", currency="EUR")
        assert wrapper.api_key == "test_key"
        assert wrapper.currency == "EUR"
    
    @patch('app.markets.cryptocompare.requests.get')
    def test_cryptocompare_get_product(self, mock_get):
        """Test get_product con mock."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'RAW': {
                'BTC': {
                    'USD': {
                        'FROMSYMBOL': 'BTC',
                        'TOSYMBOL': 'USD',
                        'PRICE': 50000.0,
                        'VOLUME24HOUR': 1000000.0
                    }
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        wrapper = CryptoCompareWrapper(api_key="test_key")
        product = wrapper.get_product("BTC")
        
        assert isinstance(product, ProductInfo)
        assert product.symbol == "BTC"
        assert product.price == 50000.0
    
    def test_cryptocompare_get_all_products_workaround(self):
        """Test che get_all_products funzioni con il workaround implementato."""
        wrapper = CryptoCompareWrapper(api_key="test_key")
        # Il metodo ora dovrebbe restituire una lista di ProductInfo invece di sollevare NotImplementedError
        products = wrapper.get_all_products()
        assert isinstance(products, list)
        # Verifica che la lista non sia vuota (dovrebbe contenere almeno alcuni asset popolari)
        assert len(products) > 0
        # Verifica che ogni elemento sia un ProductInfo
        for product in products:
            assert isinstance(product, ProductInfo)


class TestBinanceWrapper:
    """Test specifici per BinanceWrapper."""
    
    def test_binance_initialization_without_credentials(self):
        """Test che l'inizializzazione fallisca senza credenziali."""
        # Assicuriamoci che le variabili d'ambiente siano vuote per questo test
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AssertionError, match="API key is required"):
                BinanceWrapper(api_key=None, api_secret="test")
            
            with pytest.raises(AssertionError, match="API secret is required"):
                BinanceWrapper(api_key="test", api_secret=None)
    
    @patch('app.markets.binance.Client')
    def test_binance_symbol_formatting_behavior(self, mock_client):
        """Test comportamento di formattazione simbolo attraverso get_product."""
        mock_client_instance = Mock()
        mock_client_instance.get_symbol_ticker.return_value = {
            'symbol': 'BTCUSDT',
            'price': '50000.0'
        }
        mock_client_instance.get_ticker.return_value = {
            'volume': '1000000.0'
        }
        mock_client.return_value = mock_client_instance
        
        wrapper = BinanceWrapper(api_key="test", api_secret="test")
        
        # Test che entrambi i formati funzionino
        wrapper.get_product("BTC")
        wrapper.get_product("BTCUSDT")
        
        # Verifica che i metodi siano stati chiamati
        assert mock_client_instance.get_symbol_ticker.call_count == 2
    
    @patch('app.markets.binance.Client')
    def test_binance_get_product(self, mock_client):
        """Test get_product con mock."""
        mock_client_instance = Mock()
        mock_client_instance.get_symbol_ticker.return_value = {
            'symbol': 'BTCUSDT',
            'price': '50000.0'
        }
        mock_client_instance.get_ticker.return_value = {
            'volume': '1000000.0'
        }
        mock_client.return_value = mock_client_instance
        
        wrapper = BinanceWrapper(api_key="test", api_secret="test")
        product = wrapper.get_product("BTC")
        
        assert isinstance(product, ProductInfo)
        assert product.symbol == "BTC"
        assert product.price == 50000.0


class TestPublicBinanceAgent:
    """Test specifici per PublicBinanceAgent."""
    
    @patch('app.markets.binance_public.Client')
    def test_public_binance_initialization(self, mock_client):
        """Test inizializzazione senza credenziali."""
        agent = PublicBinanceAgent()
        assert agent.client is not None
        mock_client.assert_called_once_with()
    
    @patch('app.markets.binance_public.Client')
    def test_public_binance_symbol_formatting_behavior(self, mock_client):
        """Test comportamento di formattazione simbolo attraverso get_product."""
        mock_client_instance = Mock()
        mock_client_instance.get_symbol_ticker.return_value = {
            'symbol': 'BTCUSDT',
            'price': '50000.0'
        }
        mock_client_instance.get_ticker.return_value = {
            'volume': '1000000.0'
        }
        mock_client.return_value = mock_client_instance
        
        agent = PublicBinanceAgent()
        
        # Test che entrambi i formati funzionino
        agent.get_product("BTC")
        agent.get_product("BTCUSDT")
        
        # Verifica che i metodi siano stati chiamati
        assert mock_client_instance.get_symbol_ticker.call_count == 2
    
    @patch('app.markets.binance_public.Client')
    def test_public_binance_get_product(self, mock_client):
        """Test get_product con mock."""
        mock_client_instance = Mock()
        mock_client_instance.get_symbol_ticker.return_value = {
            'symbol': 'BTCUSDT',
            'price': '50000.0'
        }
        mock_client_instance.get_ticker.return_value = {
            'volume': '1000000.0'
        }
        mock_client.return_value = mock_client_instance
        
        agent = PublicBinanceAgent()
        product = agent.get_product("BTC")
        
        assert isinstance(product, ProductInfo)
        assert product.symbol == "BTC"
        assert product.price == 50000.0
    
    @patch('app.markets.binance_public.Client')
    def test_public_binance_get_all_products(self, mock_client):
        """Test get_all_products restituisce asset principali."""
        mock_client_instance = Mock()
        mock_client_instance.get_symbol_ticker.return_value = {
            'symbol': 'BTCUSDT',
            'price': '50000.0'
        }
        mock_client_instance.get_ticker.return_value = {
            'volume': '1000000.0'
        }
        mock_client.return_value = mock_client_instance
        
        agent = PublicBinanceAgent()
        products = agent.get_all_products()
        
        assert isinstance(products, list)
        assert len(products) == 8  # Numero di asset principali definiti
        for product in products:
            assert isinstance(product, ProductInfo)
    
    @patch('app.markets.binance_public.Client')
    def test_public_binance_get_public_prices(self, mock_client):
        """Test metodo specifico get_public_prices."""
        mock_client_instance = Mock()
        mock_client_instance.get_symbol_ticker.return_value = {'price': '50000.0'}
        mock_client_instance.get_server_time.return_value = {'serverTime': 1704067200000}
        mock_client.return_value = mock_client_instance
        
        agent = PublicBinanceAgent()
        prices = agent.get_public_prices(["BTCUSDT"])
        
        assert isinstance(prices, dict)
        assert 'BTC_USD' in prices
        assert prices['BTC_USD'] == 50000.0
        assert 'source' in prices
        assert prices['source'] == 'binance_public'


class TestMarketAPIs:
    """Test per la classe MarketAPIs che aggrega i wrapper."""
    
    def test_market_apis_initialization_no_providers(self):
        """Test che l'inizializzazione fallisca senza provider disponibili."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AssertionError, match="No market API keys"):
                MarketAPIs("USD")
    
    @patch('app.markets.CoinBaseWrapper')
    def test_market_apis_with_coinbase_only(self, mock_coinbase):
        """Test con solo Coinbase disponibile."""
        mock_instance = Mock()
        mock_coinbase.return_value = mock_instance
        
        with patch('app.markets.CryptoCompareWrapper', side_effect=Exception("No API key")):
            apis = MarketAPIs("USD")
            assert len(apis.wrappers) == 1
            assert apis.wrappers[0] == mock_instance
    
    @patch('app.markets.CoinBaseWrapper')
    @patch('app.markets.CryptoCompareWrapper')
    def test_market_apis_delegation(self, mock_crypto, mock_coinbase):
        """Test che i metodi vengano delegati al primo wrapper disponibile."""
        mock_coinbase_instance = Mock()
        mock_crypto_instance = Mock()
        mock_coinbase.return_value = mock_coinbase_instance
        mock_crypto.return_value = mock_crypto_instance
        
        apis = MarketAPIs("USD")
        
        # Test delegazione get_product
        apis.get_product("BTC")
        mock_coinbase_instance.get_product.assert_called_once_with("BTC")
        
        # Test delegazione get_products
        apis.get_products(["BTC", "ETH"])
        mock_coinbase_instance.get_products.assert_called_once_with(["BTC", "ETH"])
        
        # Test delegazione get_all_products
        apis.get_all_products()
        mock_coinbase_instance.get_all_products.assert_called_once()
        
        # Test delegazione get_historical_prices
        apis.get_historical_prices("BTC")
        mock_coinbase_instance.get_historical_prices.assert_called_once_with("BTC")


class TestErrorHandling:
    """Test per la gestione degli errori in tutti i wrapper."""
    
    @patch('app.markets.binance_public.Client')
    def test_public_binance_error_handling(self, mock_client):
        """Test gestione errori in PublicBinanceAgent."""
        mock_client_instance = Mock()
        mock_client_instance.get_symbol_ticker.side_effect = Exception("API Error")
        mock_client.return_value = mock_client_instance
        
        agent = PublicBinanceAgent()
        product = agent.get_product("INVALID")
        
        # Dovrebbe restituire un ProductInfo vuoto invece di sollevare eccezione
        assert isinstance(product, ProductInfo)
        assert product.id == "INVALID"
        assert product.symbol == "INVALID"
    
    @patch('app.markets.cryptocompare.requests.get')
    def test_cryptocompare_network_error(self, mock_get):
        """Test gestione errori di rete in CryptoCompareWrapper."""
        mock_get.side_effect = Exception("Network Error")
        
        wrapper = CryptoCompareWrapper(api_key="test")
        
        with pytest.raises(Exception):
            wrapper.get_product("BTC")
    
    @patch('app.markets.binance.Client')
    def test_binance_api_error_in_get_products(self, mock_client):
        """Test gestione errori in BinanceWrapper.get_products."""
        mock_client_instance = Mock()
        mock_client_instance.get_symbol_ticker.side_effect = Exception("API Error")
        mock_client.return_value = mock_client_instance
        
        wrapper = BinanceWrapper(api_key="test", api_secret="test")
        products = wrapper.get_products(["BTC", "ETH"])
        
        # Dovrebbe restituire lista vuota invece di sollevare eccezione
        assert isinstance(products, list)
        assert len(products) == 0


class TestIntegrationScenarios:
    """Test di integrazione per scenari reali."""
    
    def test_wrapper_method_signatures(self):
        """Verifica che tutti i wrapper abbiano le stesse signature dei metodi."""
        wrapper_classes = [CoinBaseWrapper, CryptoCompareWrapper, BinanceWrapper, PublicBinanceAgent]
        
        for wrapper_class in wrapper_classes:
            # Verifica get_product
            assert hasattr(wrapper_class, 'get_product')
            
            # Verifica get_products
            assert hasattr(wrapper_class, 'get_products')
            
            # Verifica get_all_products
            assert hasattr(wrapper_class, 'get_all_products')
            
            # Verifica get_historical_prices
            assert hasattr(wrapper_class, 'get_historical_prices')
    
    def test_productinfo_consistency(self):
        """Test che tutti i metodi from_* di ProductInfo restituiscano oggetti consistenti."""
        # Test from_cryptocompare
        crypto_data = {
            'FROMSYMBOL': 'BTC',
            'TOSYMBOL': 'USD', 
            'PRICE': 50000.0,
            'VOLUME24HOUR': 1000000.0
        }
        crypto_product = ProductInfo.from_cryptocompare(crypto_data)
        
        # Test from_binance
        binance_ticker = {'symbol': 'BTCUSDT', 'price': '50000.0'}
        binance_24h = {'volume': '1000000.0'}
        binance_product = ProductInfo.from_binance(binance_ticker, binance_24h)
        
        # Verifica che entrambi abbiano gli stessi campi
        assert hasattr(crypto_product, 'id')
        assert hasattr(crypto_product, 'symbol')
        assert hasattr(crypto_product, 'price')
        assert hasattr(crypto_product, 'volume_24h')
        
        assert hasattr(binance_product, 'id')
        assert hasattr(binance_product, 'symbol')
        assert hasattr(binance_product, 'price')
        assert hasattr(binance_product, 'volume_24h')
    
    def test_price_consistency(self):
        """Test che tutti i metodi from_* di Price restituiscano oggetti consistenti."""
        # Test from_cryptocompare
        crypto_data = {
            'high': 51000.0,
            'low': 49000.0,
            'open': 50000.0,
            'close': 50500.0,
            'volumeto': 1000.0,
            'time': 1704067200
        }
        crypto_price = Price.from_cryptocompare(crypto_data)
        
        # Verifica che abbia tutti i campi richiesti
        assert hasattr(crypto_price, 'high')
        assert hasattr(crypto_price, 'low')
        assert hasattr(crypto_price, 'open')
        assert hasattr(crypto_price, 'close')
        assert hasattr(crypto_price, 'volume')
        assert hasattr(crypto_price, 'time')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
