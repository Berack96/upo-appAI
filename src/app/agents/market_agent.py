from typing import Dict, List, Optional, Any
import requests
import logging
import os
from dotenv import load_dotenv
from app.signers.market_signers.coinbase_signer import CoinbaseCDPSigner
from app.signers.market_signers.cryptocompare_signer import CryptoCompareSigner

load_dotenv()
logger = logging.getLogger(__name__)


class MarketAgent:
    """
    Market Agent unificato che supporta multiple fonti di dati:
    - Coinbase Advanced Trade API (dati di mercato reali)
    - CryptoCompare (market data)
    
    Auto-configura i provider basandosi sulle variabili d'ambiente disponibili.
    """
    
    def __init__(self):
        self.providers = {}
        self._setup_providers()
        
        if not self.providers:
            logger.warning("No market data providers configured. Check your .env file.")
    
    def _setup_providers(self):
        """Configura automaticamente i provider disponibili"""
        
        # Setup Coinbase Advanced Trade API (nuovo formato)
        cdp_api_key_name = os.getenv('CDP_API_KEY_NAME')
        cdp_api_private_key = os.getenv('CDP_API_PRIVATE_KEY')
        
        if cdp_api_key_name and cdp_api_private_key:
            try:
                signer = CoinbaseCDPSigner(cdp_api_key_name, cdp_api_private_key)
                
                self.providers['coinbase'] = {
                    'type': 'coinbase_advanced_trade',
                    'signer': signer,
                    'capabilities': ['assets', 'market_data', 'trading', 'real_time_prices']
                }
                logger.info("✅ Coinbase Advanced Trade API provider configured")
                
            except Exception as e:
                logger.error(f"Failed to setup Coinbase Advanced Trade API provider: {e}")
        
        # Setup CryptoCompare se la API key è disponibile
        cryptocompare_key = os.getenv('CRYPTOCOMPARE_API_KEY')
        if cryptocompare_key:
            try:
                auth_method = os.getenv('CRYPTOCOMPARE_AUTH_METHOD', 'query')
                signer = CryptoCompareSigner(cryptocompare_key, auth_method)
                
                self.providers['cryptocompare'] = {
                    'type': 'cryptocompare',
                    'signer': signer,
                    'base_url': 'https://min-api.cryptocompare.com',
                    'capabilities': ['prices', 'historical', 'top_coins']
                }
                logger.info("✅ CryptoCompare provider configured")
                
            except Exception as e:
                logger.error(f"Failed to setup CryptoCompare provider: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Restituisce la lista dei provider configurati"""
        return list(self.providers.keys())
    
    def get_provider_capabilities(self, provider: str) -> List[str]:
        """Restituisce le capacità di un provider specifico"""
        if provider in self.providers:
            return self.providers[provider]['capabilities']
        return []
    
    # === COINBASE CDP METHODS ===
    
    def get_coinbase_asset_info(self, symbol: str) -> Dict:
        """Ottiene informazioni su un asset da Coinbase CDP"""
        if 'coinbase' not in self.providers:
            raise ValueError("Coinbase provider not configured")
        
        signer = self.providers['coinbase']['signer']
        return signer.get_asset_info(symbol)
    
    def get_coinbase_multiple_assets(self, symbols: List[str]) -> Dict:
        """Ottiene informazioni su multipli asset da Coinbase CDP"""
        if 'coinbase' not in self.providers:
            raise ValueError("Coinbase provider not configured")
        
        signer = self.providers['coinbase']['signer']
        return signer.get_multiple_assets(symbols)
    
    def get_asset_price(self, symbol: str, provider: str = None) -> Optional[float]:
        """
        Ottiene il prezzo di un asset usando il provider specificato o il primo disponibile
        """
        if provider == 'coinbase' and 'coinbase' in self.providers:
            try:
                asset_info = self.get_coinbase_asset_info(symbol)
                return float(asset_info.get('price', 0))
            except Exception as e:
                logger.error(f"Error getting {symbol} price from Coinbase: {e}")
                return None
        
        elif provider == 'cryptocompare' and 'cryptocompare' in self.providers:
            try:
                return self.get_single_crypto_price(symbol)
            except Exception as e:
                logger.error(f"Error getting {symbol} price from CryptoCompare: {e}")
                return None
        
        # Auto-select provider
        if 'cryptocompare' in self.providers:
            try:
                return self.get_single_crypto_price(symbol)
            except Exception:
                pass
        
        if 'coinbase' in self.providers:
            try:
                asset_info = self.get_coinbase_asset_info(symbol)
                return float(asset_info.get('price', 0))
            except Exception:
                pass
        
        return None
    
    # === CRYPTOCOMPARE METHODS ===
    
    def _cryptocompare_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Esegue una richiesta CryptoCompare autenticata"""
        if 'cryptocompare' not in self.providers:
            raise ValueError("CryptoCompare provider not configured")
        
        provider = self.providers['cryptocompare']
        request_data = provider['signer'].prepare_request(
            provider['base_url'], endpoint, params
        )
        
        response = requests.get(
            request_data['url'],
            headers=request_data['headers'],
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def get_crypto_prices(self, from_symbols: List[str], to_symbols: List[str] = None) -> Dict:
        """Ottiene prezzi da CryptoCompare"""
        if to_symbols is None:
            to_symbols = ["USD", "EUR"]
        
        params = {
            "fsyms": ",".join(from_symbols),
            "tsyms": ",".join(to_symbols)
        }
        
        return self._cryptocompare_request("/data/pricemulti", params)
    
    def get_single_crypto_price(self, from_symbol: str, to_symbol: str = "USD") -> float:
        """Ottiene il prezzo di una singola crypto da CryptoCompare"""
        params = {
            "fsym": from_symbol,
            "tsyms": to_symbol
        }
        
        data = self._cryptocompare_request("/data/price", params)
        return data.get(to_symbol, 0.0)
    
    def get_top_cryptocurrencies(self, limit: int = 10, to_symbol: str = "USD") -> Dict:
        """Ottiene le top crypto per market cap da CryptoCompare"""
        params = {
            "limit": str(limit),
            "tsym": to_symbol
        }
        
        return self._cryptocompare_request("/data/top/mktcapfull", params)
    
    # === UNIFIED INTERFACE ===
    
    def get_market_overview(self, symbols: List[str] = None) -> Dict:
        """
        Ottiene una panoramica del mercato usando il miglior provider disponibile
        """
        if symbols is None:
            symbols = ["BTC", "ETH", "ADA"]
        
        result = {
            "timestamp": None,
            "data": {},
            "source": None,
            "providers_used": []
        }
        
        # Prova CryptoCompare per prezzi multipli (più completo)
        if 'cryptocompare' in self.providers:
            try:
                prices = self.get_crypto_prices(symbols, ["USD", "EUR"])
                result["data"] = prices
                result["source"] = "cryptocompare"
                result["providers_used"].append("cryptocompare")
                logger.info("Market overview retrieved from CryptoCompare")
            except Exception as e:
                logger.warning(f"CryptoCompare failed, trying fallback: {e}")
        
        # Fallback a Coinbase Advanced Trade se CryptoCompare fallisce
        if not result["data"] and 'coinbase' in self.providers:
            try:
                # Usa il nuovo metodo Advanced Trade per ottenere multipli asset
                coinbase_data = self.get_coinbase_multiple_assets(symbols)
                if coinbase_data:
                    # Trasforma i dati Advanced Trade nel formato standard
                    formatted_data = {}
                    for symbol in symbols:
                        if symbol in coinbase_data:
                            formatted_data[symbol] = {
                                "USD": coinbase_data[symbol].get("price", 0)
                            }
                    
                    result["data"] = formatted_data
                    result["source"] = "coinbase_advanced_trade"
                    result["providers_used"].append("coinbase")
                    logger.info("Market overview retrieved from Coinbase Advanced Trade API")
            except Exception as e:
                logger.error(f"Coinbase Advanced Trade fallback failed: {e}")
        
        return result
    
    def analyze(self, query: str) -> str:
        """
        Analizza il mercato usando tutti i provider disponibili
        """
        if not self.providers:
            return "⚠️ Nessun provider di dati di mercato configurato. Controlla il file .env."
        
        try:
            # Ottieni panoramica del mercato
            overview = self.get_market_overview(["BTC", "ETH", "ADA", "DOT"])
            
            if not overview["data"]:
                return "⚠️ Impossibile recuperare dati di mercato da nessun provider."
            
            # Formatta i risultati
            result_lines = [
                f"📊 **Market Analysis** (via {overview['source'].upper()})\n"
            ]
            
            for crypto, prices in overview["data"].items():
                if isinstance(prices, dict):
                    usd_price = prices.get("USD", "N/A")
                    eur_price = prices.get("EUR", "N/A")
                    if eur_price != "N/A":
                        result_lines.append(f"**{crypto}**: ${usd_price} (€{eur_price})")
                    else:
                        result_lines.append(f"**{crypto}**: ${usd_price}")
            
            # Aggiungi info sui provider
            providers_info = f"\n🔧 **Available providers**: {', '.join(self.get_available_providers())}"
            result_lines.append(providers_info)
            
            return "\n".join(result_lines)
            
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            return f"⚠️ Errore nell'analisi del mercato: {e}"
