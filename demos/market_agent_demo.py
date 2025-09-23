#!/usr/bin/env python3
"""
Esempio di utilizzo del MarketAgent unificato.
Questo script mostra come utilizzare il nuovo MarketAgent che supporta
multiple fonti di dati (Coinbase e CryptoCompare).
"""

import sys
from pathlib import Path

# Aggiungi il path src al PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
from app.agents.market_agent import MarketAgent

# Carica variabili d'ambiente
load_dotenv()

def main():
    print("🚀 Market Agent Demo\n")
    
    try:
        # Inizializza il market agent (auto-configura i provider disponibili)
        agent = MarketAgent()
        
        # Mostra provider disponibili
        providers = agent.get_available_providers()
        print(f"📡 Available providers: {providers}")
        
        if not providers:
            print("❌ No providers configured. Please check your .env file.")
            print("Required variables:")
            print("  For Coinbase: COINBASE_API_KEY, COINBASE_SECRET, COINBASE_PASSPHRASE")
            print("  For CryptoCompare: CRYPTOCOMPARE_API_KEY")
            return
        
        # Mostra le capacità di ogni provider
        print("\n🔧 Provider capabilities:")
        for provider in providers:
            capabilities = agent.get_provider_capabilities(provider)
            print(f"  {provider}: {capabilities}")
        
        # Ottieni panoramica del mercato
        print("\n📊 Market Overview:")
        overview = agent.get_market_overview(["BTC", "ETH", "ADA"])
        print(f"Data source: {overview.get('source', 'Unknown')}")
        
        for crypto, prices in overview.get('data', {}).items():
            if isinstance(prices, dict):
                usd = prices.get('USD', 'N/A')
                eur = prices.get('EUR', 'N/A')
                if eur != 'N/A':
                    print(f"  {crypto}: ${usd} (€{eur})")
                else:
                    print(f"  {crypto}: ${usd}")
        
        # Analisi completa del mercato
        print("\n📈 Market Analysis:")
        analysis = agent.analyze("comprehensive market analysis")
        print(analysis)
        
        # Test specifici per provider (se disponibili)
        if 'cryptocompare' in providers:
            print("\n🔸 CryptoCompare specific test:")
            try:
                btc_price = agent.get_single_crypto_price("BTC", "USD")
                print(f"  BTC price: ${btc_price}")
                
                top_coins = agent.get_top_cryptocurrencies(5)
                if top_coins.get('Data'):
                    print("  Top 5 cryptocurrencies by market cap:")
                    for coin in top_coins['Data'][:3]:  # Show top 3
                        coin_info = coin.get('CoinInfo', {})
                        display = coin.get('DISPLAY', {}).get('USD', {})
                        name = coin_info.get('FullName', 'Unknown')
                        price = display.get('PRICE', 'N/A')
                        print(f"    {name}: {price}")
            except Exception as e:
                print(f"  CryptoCompare test failed: {e}")
        
        if 'coinbase' in providers:
            print("\n🔸 Coinbase specific test:")
            try:
                ticker = agent.get_coinbase_ticker("BTC-USD")
                price = ticker.get('price', 'N/A')
                volume = ticker.get('volume_24h', 'N/A')
                print(f"  BTC-USD: ${price} (24h volume: {volume})")
            except Exception as e:
                print(f"  Coinbase test failed: {e}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure you have configured at least one provider in your .env file.")

if __name__ == "__main__":
    main()