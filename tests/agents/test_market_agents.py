#!/usr/bin/env python3
"""
Test suite per il MarketAgent unificato.
Compatibile con pytest per l'esecuzione automatizzata dei test.
"""

import os
import sys
import pytest
from pathlib import Path

# Aggiungi il path src al PYTHONPATH per gli import
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()


class TestMarketAgent:
    """Test suite per il MarketAgent unificato"""
    
    @pytest.fixture(scope="class")
    def market_agent(self):
        """Fixture per inizializzare il MarketAgent"""
        from app.agents.market_agent import MarketAgent
        return MarketAgent()
    
    def test_agent_initialization(self, market_agent):
        """Testa che l'agent si inizializzi correttamente"""
        assert market_agent is not None
        providers = market_agent.get_available_providers()
        assert isinstance(providers, list)
    
    def test_providers_configuration(self, market_agent):
        """Testa che almeno un provider sia configurato"""
        providers = market_agent.get_available_providers()
        
        # Se nessun provider è configurato, skippa i test
        if not providers:
            pytest.skip("No market data providers configured. Check your .env file.")
        
        assert len(providers) > 0
        print(f"Available providers: {providers}")
    
    def test_provider_capabilities(self, market_agent):
        """Testa che ogni provider abbia delle capacità definite"""
        providers = market_agent.get_available_providers()
        
        if not providers:
            pytest.skip("No providers configured")
        
        for provider in providers:
            capabilities = market_agent.get_provider_capabilities(provider)
            assert isinstance(capabilities, list)
            assert len(capabilities) > 0
            print(f"{provider} capabilities: {capabilities}")
    
    def test_market_overview(self, market_agent):
        """Testa la funzionalità di panoramica del mercato"""
        providers = market_agent.get_available_providers()
        
        if not providers:
            pytest.skip("No providers configured")
        
        overview = market_agent.get_market_overview(["BTC", "ETH"])
        
        assert isinstance(overview, dict)
        assert "data" in overview
        assert "source" in overview
        assert "providers_used" in overview
        
        # Se abbiamo dati, verifichiamo la struttura
        if overview.get("data"):
            assert isinstance(overview["data"], dict)
            assert overview.get("source") is not None
            print(f"Market overview source: {overview.get('source')}")
    
    def test_market_analysis(self, market_agent):
        """Testa la funzione di analisi del mercato"""
        providers = market_agent.get_available_providers()
        
        if not providers:
            pytest.skip("No providers configured")
        
        analysis = market_agent.analyze("market overview")
        
        assert isinstance(analysis, str)
        assert len(analysis) > 0
        assert not analysis.startswith("⚠️ Nessun provider")
        print(f"Analysis preview: {analysis[:100]}...")
    
    @pytest.mark.skipif(
        not os.getenv('CRYPTOCOMPARE_API_KEY'), 
        reason="CRYPTOCOMPARE_API_KEY not configured"
    )
    def test_cryptocompare_specific_methods(self, market_agent):
        """Testa i metodi specifici di CryptoCompare"""
        providers = market_agent.get_available_providers()
        
        if 'cryptocompare' not in providers:
            pytest.skip("CryptoCompare provider not available")
        
        # Test single price
        btc_price = market_agent.get_single_crypto_price("BTC", "USD")
        assert isinstance(btc_price, (int, float))
        assert btc_price > 0
        print(f"BTC Price (CryptoCompare): ${btc_price}")
        
        # Test multiple prices
        prices = market_agent.get_crypto_prices(["BTC", "ETH"], ["USD"])
        assert isinstance(prices, dict)
        assert "BTC" in prices or "ETH" in prices
        
        # Test top cryptocurrencies
        top_coins = market_agent.get_top_cryptocurrencies(5)
        assert isinstance(top_coins, dict)
    
    @pytest.mark.skipif(
        not (
            (os.getenv('COINBASE_API_KEY') and os.getenv('COINBASE_PRIVATE_KEY')) or
            (os.getenv('COINBASE_API_KEY') and os.getenv('COINBASE_SECRET') and os.getenv('COINBASE_PASSPHRASE'))
        ), 
        reason="Coinbase credentials not configured (need either new format: API_KEY+PRIVATE_KEY or legacy: API_KEY+SECRET+PASSPHRASE)"
    )
    def test_coinbase_specific_methods(self, market_agent):
        """Testa i metodi specifici di Coinbase"""
        providers = market_agent.get_available_providers()
        
        if 'coinbase' not in providers:
            pytest.skip("Coinbase provider not available")
        
        # Test ticker
        ticker = market_agent.get_coinbase_ticker("BTC-USD")
        assert isinstance(ticker, dict)
        assert "price" in ticker
        
        price = float(ticker.get("price", 0))
        assert price > 0
        print(f"BTC Price (Coinbase): ${price}")
    
    def test_fallback_mechanism(self, market_agent):
        """Testa il meccanismo di fallback tra provider"""
        providers = market_agent.get_available_providers()
        
        if len(providers) < 2:
            pytest.skip("Need at least 2 providers to test fallback")
        
        # Il test del fallback è implicito nel get_market_overview
        # che prova CryptoCompare prima e poi Coinbase
        overview = market_agent.get_market_overview(["BTC"])
        
        assert overview.get("data") is not None
        assert len(overview.get("providers_used", [])) > 0
    
    def test_error_handling(self, market_agent):
        """Testa la gestione degli errori"""
        providers = market_agent.get_available_providers()
        
        if not providers:
            pytest.skip("No providers configured")
        
        # Test con simbolo crypto inesistente
        overview = market_agent.get_market_overview(["NONEXISTENT_CRYPTO"])
        
        # Dovrebbe gestire l'errore gracefully
        assert isinstance(overview, dict)
        # I dati potrebbero essere vuoti ma non dovrebbe crashare
