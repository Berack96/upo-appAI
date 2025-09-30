#!/usr/bin/env python3
"""
Demo Completo per Market Data Providers
========================================

Questo script dimostra l'utilizzo di tutti i wrapper che implementano BaseWrapper:
- CoinBaseWrapper (richiede credenziali)
- CryptoCompareWrapper (richiede API key)
- BinanceWrapper (richiede credenziali)
- PublicBinanceAgent (accesso pubblico)

Lo script effettua chiamate GET a diversi provider e visualizza i dati
in modo strutturato con informazioni dettagliate su timestamp, stato
delle richieste e formattazione tabellare.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import traceback

# Aggiungi il path src al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from dotenv import load_dotenv
from src.app.markets import (
    CoinBaseWrapper, 
    CryptoCompareWrapper, 
    BinanceWrapper, 
    PublicBinanceAgent,
    BaseWrapper
)

# Carica variabili d'ambiente
load_dotenv()

class DemoFormatter:
    """Classe per formattare l'output del demo in modo strutturato."""
    
    @staticmethod
    def print_header(title: str, char: str = "=", width: int = 80):
        """Stampa un'intestazione formattata."""
        print(f"\n{char * width}")
        print(f"{title:^{width}}")
        print(f"{char * width}")
    
    @staticmethod
    def print_subheader(title: str, char: str = "-", width: int = 60):
        """Stampa una sotto-intestazione formattata."""
        print(f"\n{char * width}")
        print(f" {title}")
        print(f"{char * width}")
    
    @staticmethod
    def print_request_info(provider_name: str, method: str, timestamp: datetime, 
                          status: str, error: Optional[str] = None):
        """Stampa informazioni sulla richiesta."""
        print(f"🕒 Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏷️  Provider: {provider_name}")
        print(f"🔧 Method: {method}")
        print(f"📊 Status: {status}")
        if error:
            print(f"❌ Error: {error}")
        print()
    
    @staticmethod
    def print_product_table(products: List[Any], title: str = "Products"):
        """Stampa una tabella di prodotti."""
        if not products:
            print(f"📋 {title}: Nessun prodotto trovato")
            return
        
        print(f"📋 {title} ({len(products)} items):")
        print(f"{'Symbol':<15} {'ID':<20} {'Price':<12} {'Quote':<10} {'Status':<10}")
        print("-" * 67)
        
        for product in products[:10]:  # Mostra solo i primi 10
            symbol = getattr(product, 'symbol', 'N/A')
            product_id = getattr(product, 'id', 'N/A')
            price = getattr(product, 'price', 0.0)
            quote = getattr(product, 'quote_currency', 'N/A')
            status = getattr(product, 'status', 'N/A')
            
            # Tronca l'ID se troppo lungo
            if len(product_id) > 18:
                product_id = product_id[:15] + "..."
            
            price_str = f"${price:.2f}" if price > 0 else "N/A"
            
            print(f"{symbol:<15} {product_id:<20} {price_str:<12} {quote:<10} {status:<10}")
        
        if len(products) > 10:
            print(f"... e altri {len(products) - 10} prodotti")
        print()
    
    @staticmethod
    def print_prices_table(prices: List[Any], title: str = "Historical Prices"):
        """Stampa una tabella di prezzi storici."""
        if not prices:
            print(f"💰 {title}: Nessun prezzo trovato")
            return
        
        print(f"💰 {title} ({len(prices)} entries):")
        print(f"{'Time':<12} {'Open':<12} {'High':<12} {'Low':<12} {'Close':<12} {'Volume':<15}")
        print("-" * 75)
        
        for price in prices[:5]:  # Mostra solo i primi 5
            time_str = getattr(price, 'time', 'N/A')
            # Il time è già una stringa, non serve strftime
            if len(time_str) > 10:
                time_str = time_str[:10]  # Tronca se troppo lungo
            
            open_price = f"${getattr(price, 'open', 0):.2f}"
            high_price = f"${getattr(price, 'high', 0):.2f}"
            low_price = f"${getattr(price, 'low', 0):.2f}"
            close_price = f"${getattr(price, 'close', 0):.2f}"
            volume = f"{getattr(price, 'volume', 0):,.0f}"
            
            print(f"{time_str:<12} {open_price:<12} {high_price:<12} {low_price:<12} {close_price:<12} {volume:<15}")
        
        if len(prices) > 5:
            print(f"... e altri {len(prices) - 5} prezzi")
        print()

class ProviderTester:
    """Classe per testare i provider di market data."""
    
    def __init__(self):
        self.formatter = DemoFormatter()
        self.test_symbols = ["BTC", "ETH", "ADA"]
    
    def test_provider(self, wrapper: BaseWrapper, provider_name: str) -> Dict[str, Any]:
        """Testa un provider specifico con tutti i metodi disponibili."""
        results = {
            "provider_name": provider_name,
            "tests": {},
            "overall_status": "SUCCESS"
        }
        
        self.formatter.print_subheader(f"🔍 Testing {provider_name}")
        
        # Test get_product
        for symbol in self.test_symbols:
            timestamp = datetime.now()
            try:
                product = wrapper.get_product(symbol)
                self.formatter.print_request_info(
                    provider_name, f"get_product({symbol})", timestamp, "✅ SUCCESS"
                )
                if product:
                    print(f"📦 Product: {product.symbol} (ID: {product.id})")
                    print(f"   Price: ${product.price:.2f}, Quote: {product.quote_currency}")
                    print(f"   Status: {product.status}, Volume 24h: {product.volume_24h:,.2f}")
                else:
                    print(f"📦 Product: Nessun prodotto trovato per {symbol}")
                
                results["tests"][f"get_product_{symbol}"] = "SUCCESS"
                
            except Exception as e:
                error_msg = str(e)
                self.formatter.print_request_info(
                    provider_name, f"get_product({symbol})", timestamp, "❌ ERROR", error_msg
                )
                results["tests"][f"get_product_{symbol}"] = f"ERROR: {error_msg}"
                results["overall_status"] = "PARTIAL"
        
        # Test get_products
        timestamp = datetime.now()
        try:
            products = wrapper.get_products(self.test_symbols)
            self.formatter.print_request_info(
                provider_name, f"get_products({self.test_symbols})", timestamp, "✅ SUCCESS"
            )
            self.formatter.print_product_table(products, f"{provider_name} Products")
            results["tests"]["get_products"] = "SUCCESS"
            
        except Exception as e:
            error_msg = str(e)
            self.formatter.print_request_info(
                provider_name, f"get_products({self.test_symbols})", timestamp, "❌ ERROR", error_msg
            )
            results["tests"]["get_products"] = f"ERROR: {error_msg}"
            results["overall_status"] = "PARTIAL"
        
        # Test get_all_products
        timestamp = datetime.now()
        try:
            all_products = wrapper.get_all_products()
            self.formatter.print_request_info(
                provider_name, "get_all_products()", timestamp, "✅ SUCCESS"
            )
            self.formatter.print_product_table(all_products, f"{provider_name} All Products")
            results["tests"]["get_all_products"] = "SUCCESS"
            
        except Exception as e:
            error_msg = str(e)
            self.formatter.print_request_info(
                provider_name, "get_all_products()", timestamp, "❌ ERROR", error_msg
            )
            results["tests"]["get_all_products"] = f"ERROR: {error_msg}"
            results["overall_status"] = "PARTIAL"
        
        # Test get_historical_prices
        timestamp = datetime.now()
        try:
            prices = wrapper.get_historical_prices("BTC")
            self.formatter.print_request_info(
                provider_name, "get_historical_prices(BTC)", timestamp, "✅ SUCCESS"
            )
            self.formatter.print_prices_table(prices, f"{provider_name} BTC Historical Prices")
            results["tests"]["get_historical_prices"] = "SUCCESS"
            
        except Exception as e:
            error_msg = str(e)
            self.formatter.print_request_info(
                provider_name, "get_historical_prices(BTC)", timestamp, "❌ ERROR", error_msg
            )
            results["tests"]["get_historical_prices"] = f"ERROR: {error_msg}"
            results["overall_status"] = "PARTIAL"
        
        return results

def check_environment_variables() -> Dict[str, bool]:
    """Verifica la presenza delle variabili d'ambiente necessarie."""
    env_vars = {
        "COINBASE_API_KEY": bool(os.getenv("COINBASE_API_KEY")),
        "COINBASE_API_SECRET": bool(os.getenv("COINBASE_API_SECRET")),
        "CRYPTOCOMPARE_API_KEY": bool(os.getenv("CRYPTOCOMPARE_API_KEY")),
        "BINANCE_API_KEY": bool(os.getenv("BINANCE_API_KEY")),
        "BINANCE_API_SECRET": bool(os.getenv("BINANCE_API_SECRET")),
    }
    return env_vars

def initialize_providers() -> Dict[str, BaseWrapper]:
    """Inizializza tutti i provider disponibili."""
    providers = {}
    env_vars = check_environment_variables()
    
    # PublicBinanceAgent (sempre disponibile)
    try:
        providers["PublicBinance"] = PublicBinanceAgent()
        print("✅ PublicBinanceAgent inizializzato con successo")
    except Exception as e:
        print(f"❌ Errore nell'inizializzazione di PublicBinanceAgent: {e}")
    
    # CryptoCompareWrapper
    if env_vars["CRYPTOCOMPARE_API_KEY"]:
        try:
            providers["CryptoCompare"] = CryptoCompareWrapper()
            print("✅ CryptoCompareWrapper inizializzato con successo")
        except Exception as e:
            print(f"❌ Errore nell'inizializzazione di CryptoCompareWrapper: {e}")
    else:
        print("⚠️ CryptoCompareWrapper saltato: CRYPTOCOMPARE_API_KEY non trovata")
    
    # CoinBaseWrapper
    if env_vars["COINBASE_API_KEY"] and env_vars["COINBASE_API_SECRET"]:
        try:
            providers["CoinBase"] = CoinBaseWrapper()
            print("✅ CoinBaseWrapper inizializzato con successo")
        except Exception as e:
            print(f"❌ Errore nell'inizializzazione di CoinBaseWrapper: {e}")
    else:
        print("⚠️ CoinBaseWrapper saltato: credenziali Coinbase non complete")
    
    # BinanceWrapper
    if env_vars["BINANCE_API_KEY"] and env_vars["BINANCE_API_SECRET"]:
        try:
            providers["Binance"] = BinanceWrapper()
            print("✅ BinanceWrapper inizializzato con successo")
        except Exception as e:
            print(f"❌ Errore nell'inizializzazione di BinanceWrapper: {e}")
    else:
        print("⚠️ BinanceWrapper saltato: credenziali Binance non complete")
    
    return providers

def print_summary(results: List[Dict[str, Any]]):
    """Stampa un riassunto finale dei risultati."""
    formatter = DemoFormatter()
    formatter.print_header("📊 RIASSUNTO FINALE", "=", 80)
    
    total_providers = len(results)
    successful_providers = sum(1 for r in results if r["overall_status"] == "SUCCESS")
    partial_providers = sum(1 for r in results if r["overall_status"] == "PARTIAL")
    
    print(f"🔢 Provider testati: {total_providers}")
    print(f"✅ Provider completamente funzionanti: {successful_providers}")
    print(f"⚠️ Provider parzialmente funzionanti: {partial_providers}")
    print(f"❌ Provider non funzionanti: {total_providers - successful_providers - partial_providers}")
    
    print("\n📋 Dettaglio per provider:")
    for result in results:
        provider_name = result["provider_name"]
        status = result["overall_status"]
        status_icon = "✅" if status == "SUCCESS" else "⚠️" if status == "PARTIAL" else "❌"
        
        print(f"\n{status_icon} {provider_name}:")
        for test_name, test_result in result["tests"].items():
            test_icon = "✅" if test_result == "SUCCESS" else "❌"
            print(f"   {test_icon} {test_name}: {test_result}")

def main():
    """Funzione principale del demo."""
    formatter = DemoFormatter()
    
    # Intestazione principale
    formatter.print_header("🚀 DEMO COMPLETO MARKET DATA PROVIDERS", "=", 80)
    
    print(f"🕒 Avvio demo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Questo demo testa tutti i wrapper BaseWrapper disponibili")
    print("🔍 Ogni test include timestamp, stato della richiesta e dati formattati")
    
    # Verifica variabili d'ambiente
    formatter.print_subheader("🔐 Verifica Configurazione")
    env_vars = check_environment_variables()
    
    print("Variabili d'ambiente:")
    for var_name, is_present in env_vars.items():
        status = "✅ Presente" if is_present else "❌ Mancante"
        print(f"  {var_name}: {status}")
    
    # Inizializza provider
    formatter.print_subheader("🏗️ Inizializzazione Provider")
    providers = initialize_providers()
    
    if not providers:
        print("❌ Nessun provider disponibile. Verifica la configurazione.")
        return
    
    print(f"\n🎯 Provider disponibili per il test: {list(providers.keys())}")
    
    # Testa ogni provider
    formatter.print_header("🧪 ESECUZIONE TEST PROVIDER", "=", 80)
    
    tester = ProviderTester()
    all_results = []
    
    for provider_name, wrapper in providers.items():
        try:
            result = tester.test_provider(wrapper, provider_name)
            all_results.append(result)
        except Exception as e:
            print(f"❌ Errore critico nel test di {provider_name}: {e}")
            traceback.print_exc()
            all_results.append({
                "provider_name": provider_name,
                "tests": {},
                "overall_status": "CRITICAL_ERROR",
                "error": str(e)
            })
    
    # Stampa riassunto finale
    print_summary(all_results)
    
    # Informazioni aggiuntive
    formatter.print_header("ℹ️ INFORMAZIONI AGGIUNTIVE", "=", 80)
    print("📚 Documentazione:")
    print("   - BaseWrapper: src/app/markets/base.py")
    print("   - Test completi: tests/agents/test_market.py")
    print("   - Configurazione: .env")
    
    print("\n🔧 Per abilitare tutti i provider:")
    print("   1. Configura le credenziali nel file .env")
    print("   2. Segui la documentazione di ogni provider")
    print("   3. Riavvia il demo")
    
    print(f"\n🏁 Demo completato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()