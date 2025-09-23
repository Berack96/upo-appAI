#!/usr/bin/env python3
"""
Demo script per testare il MarketAgent aggiornato con Coinbase CDP
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.app.agents.market_agent import MarketAgent
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("🚀 Test MarketAgent con Coinbase CDP")
    print("=" * 50)
    
    # Inizializza l'agent
    agent = MarketAgent()
    
    # Verifica provider disponibili
    providers = agent.get_available_providers()
    print(f"📡 Provider disponibili: {providers}")
    
    if not providers:
        print("⚠️ Nessun provider configurato. Verifica il file .env")
        print("\nPer Coinbase CDP, serve:")
        print("CDP_API_KEY_NAME=your_key_name")
        print("CDP_API_PRIVATE_KEY=your_private_key")
        print("\nPer CryptoCompare, serve:")
        print("CRYPTOCOMPARE_API_KEY=your_api_key")
        return
    
    # Mostra capabilities di ogni provider
    for provider in providers:
        capabilities = agent.get_provider_capabilities(provider)
        print(f"🔧 {provider.upper()}: {capabilities}")
    
    print("\n" + "=" * 50)
    
    # Test ottenimento prezzo singolo
    test_symbols = ["BTC", "ETH", "ADA"]
    
    for symbol in test_symbols:
        print(f"\n💰 Prezzo {symbol}:")
        
        # Prova ogni provider
        for provider in providers:
            try:
                price = agent.get_asset_price(symbol, provider)
                if price:
                    print(f"  {provider}: ${price:,.2f}")
                else:
                    print(f"  {provider}: N/A")
            except Exception as e:
                print(f"  {provider}: Errore - {e}")
    
    print("\n" + "=" * 50)
    
    # Test market overview
    print("\n📊 Market Overview:")
    try:
        overview = agent.get_market_overview(["BTC", "ETH", "ADA", "DOT"])
        
        if overview["data"]:
            print(f"📡 Fonte: {overview['source']}")
            
            for crypto, prices in overview["data"].items():
                if isinstance(prices, dict):
                    usd_price = prices.get("USD", "N/A")
                    eur_price = prices.get("EUR", "N/A")
                    
                    if eur_price != "N/A":
                        print(f"  {crypto}: ${usd_price} (€{eur_price})")
                    else:
                        print(f"  {crypto}: ${usd_price}")
        else:
            print("⚠️ Nessun dato disponibile")
            
    except Exception as e:
        print(f"❌ Errore nel market overview: {e}")
    
    print("\n" + "=" * 50)
    
    # Test funzione analyze
    print("\n🔍 Analisi mercato:")
    try:
        analysis = agent.analyze("Market overview")
        print(analysis)
    except Exception as e:
        print(f"❌ Errore nell'analisi: {e}")
    
    # Test specifico Coinbase CDP se disponibile
    if 'coinbase' in providers:
        print("\n" + "=" * 50)
        print("\n🏦 Test specifico Coinbase CDP:")
        
        try:
            # Test asset singolo
            btc_info = agent.get_coinbase_asset_info("BTC")
            print(f"📈 BTC Info: {btc_info}")
            
            # Test asset multipli
            multi_assets = agent.get_coinbase_multiple_assets(["BTC", "ETH"])
            print(f"📊 Multi Assets: {multi_assets}")
            
        except Exception as e:
            print(f"❌ Errore nel test Coinbase CDP: {e}")

if __name__ == "__main__":
    main()