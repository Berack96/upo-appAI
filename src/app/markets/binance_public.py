"""
Versione pubblica di Binance per accesso ai dati pubblici senza autenticazione.

Questa implementazione estende BaseWrapper per mantenere coerenza
con l'architettura del modulo markets.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from binance.client import Client
from app.markets.base import BaseWrapper, ProductInfo, Price
from app.markets.error_handler import retry_on_failure, handle_api_errors, MarketAPIError


class PublicBinanceAgent(BaseWrapper):
    """
    Agent per l'accesso ai dati pubblici di Binance.
    
    Utilizza l'API pubblica di Binance per ottenere informazioni
    sui prezzi e sui mercati senza richiedere autenticazione.
    """
    
    def __init__(self):
        """Inizializza il client pubblico senza credenziali."""
        self.client = Client()

    def __format_symbol(self, asset_id: str) -> str:
        """
        Formatta l'asset_id per Binance (es. BTC -> BTCUSDT).
        
        Args:
            asset_id: ID dell'asset (es. "BTC", "ETH")
        
        Returns:
            Simbolo formattato per Binance
        """
        if asset_id.endswith("USDT") or asset_id.endswith("BUSD"):
            return asset_id
        return f"{asset_id}USDT"

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_product(self, asset_id: str) -> ProductInfo:
        """
        Ottiene informazioni su un singolo prodotto.
        
        Args:
            asset_id: ID dell'asset (es. "BTC")
        
        Returns:
            Oggetto ProductInfo con le informazioni del prodotto
        """
        symbol = self.__format_symbol(asset_id)
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            ticker_24h = self.client.get_ticker(symbol=symbol)
            return ProductInfo.from_binance(ticker, ticker_24h)
        except Exception as e:
            print(f"Errore nel recupero del prodotto {asset_id}: {e}")
            return ProductInfo(id=asset_id, symbol=asset_id)

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        """
        Ottiene informazioni su più prodotti.
        
        Args:
            asset_ids: Lista di ID degli asset
        
        Returns:
            Lista di oggetti ProductInfo
        """
        products = []
        for asset_id in asset_ids:
            product = self.get_product(asset_id)
            products.append(product)
        return products

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_all_products(self) -> list[ProductInfo]:
        """
        Ottiene informazioni su tutti i prodotti disponibili.
        
        Returns:
            Lista di oggetti ProductInfo per i principali asset
        """
        # Per la versione pubblica, restituiamo solo i principali asset
        major_assets = ["BTC", "ETH", "BNB", "ADA", "DOT", "LINK", "LTC", "XRP"]
        return self.get_products(major_assets)

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_historical_prices(self, asset_id: str = "BTC") -> list[Price]:
        """
        Ottiene i prezzi storici per un asset.
        
        Args:
            asset_id: ID dell'asset (default: "BTC")
        
        Returns:
            Lista di oggetti Price con i dati storici
        """
        symbol = self.__format_symbol(asset_id)
        try:
            # Ottieni candele degli ultimi 30 giorni
            end_time = datetime.now()
            start_time = end_time - timedelta(days=30)
            
            klines = self.client.get_historical_klines(
                symbol, 
                Client.KLINE_INTERVAL_1DAY,
                start_time.strftime("%d %b %Y %H:%M:%S"),
                end_time.strftime("%d %b %Y %H:%M:%S")
            )
            
            prices = []
            for kline in klines:
                price = Price(
                    open=float(kline[1]),
                    high=float(kline[2]),
                    low=float(kline[3]),
                    close=float(kline[4]),
                    volume=float(kline[5]),
                    time=str(datetime.fromtimestamp(kline[0] / 1000))
                )
                prices.append(price)
            
            return prices
        except Exception as e:
            print(f"Errore nel recupero dei prezzi storici per {asset_id}: {e}")
            return []

    def get_public_prices(self, symbols: Optional[list[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Ottiene i prezzi pubblici per i simboli specificati.
        
        Args:
            symbols: Lista di simboli da recuperare (es. ["BTCUSDT", "ETHUSDT"]).
                    Se None, recupera BTC e ETH di default.
        
        Returns:
            Dizionario con i prezzi e informazioni sulla fonte, o None in caso di errore.
        """
        if symbols is None:
            symbols = ["BTCUSDT", "ETHUSDT"]
        
        try:
            prices = {}
            for symbol in symbols:
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                # Converte BTCUSDT -> BTC_USD per consistenza
                clean_symbol = symbol.replace("USDT", "_USD").replace("BUSD", "_USD")
                prices[clean_symbol] = float(ticker['price'])
            
            return {
                **prices,
                'source': 'binance_public',
                'timestamp': self.client.get_server_time()['serverTime']
            }
        except Exception as e:
            print(f"Errore nel recupero dei prezzi pubblici: {e}")
            return None

    def get_24hr_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Ottiene le statistiche 24h per un simbolo specifico.
        
        Args:
            symbol: Simbolo del trading pair (es. "BTCUSDT")
        
        Returns:
            Dizionario con le statistiche 24h o None in caso di errore.
        """
        try:
            ticker = self.client.get_ticker(symbol=symbol)
            return {
                'symbol': ticker['symbol'],
                'price': float(ticker['lastPrice']),
                'price_change': float(ticker['priceChange']),
                'price_change_percent': float(ticker['priceChangePercent']),
                'high_24h': float(ticker['highPrice']),
                'low_24h': float(ticker['lowPrice']),
                'volume_24h': float(ticker['volume']),
                'source': 'binance_public'
            }
        except Exception as e:
            print(f"Errore nel recupero del ticker 24h per {symbol}: {e}")
            return None

    def get_exchange_info(self) -> Optional[Dict[str, Any]]:
        """
        Ottiene informazioni generali sull'exchange.
        
        Returns:
            Dizionario con informazioni sull'exchange o None in caso di errore.
        """
        try:
            info = self.client.get_exchange_info()
            return {
                'timezone': info['timezone'],
                'server_time': info['serverTime'],
                'symbols_count': len(info['symbols']),
                'source': 'binance_public'
            }
        except Exception as e:
            print(f"Errore nel recupero delle informazioni exchange: {e}")
            return None


# Esempio di utilizzo
if __name__ == "__main__":
    # Uso senza credenziali
    public_agent = PublicBinanceAgent()
    
    # Ottieni prezzi di default (BTC e ETH)
    public_prices = public_agent.get_public_prices()
    print("Prezzi pubblici:", public_prices)
    
    # Ottieni statistiche 24h per BTC
    btc_stats = public_agent.get_24hr_ticker("BTCUSDT")
    print("Statistiche BTC 24h:", btc_stats)
    
    # Ottieni informazioni exchange
    exchange_info = public_agent.get_exchange_info()
    print("Info exchange:", exchange_info)