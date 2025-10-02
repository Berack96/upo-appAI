import os
from typing import Optional
from datetime import datetime, timedelta
from binance.client import Client
from base import ProductInfo, BaseWrapper, Price
from error_handler import retry_on_failure, handle_api_errors, MarketAPIError


class BinanceWrapper(BaseWrapper):
    """
    Wrapper per le API autenticate di Binance.
    
    Implementa l'interfaccia BaseWrapper per fornire accesso unificato
    ai dati di mercato di Binance tramite le API REST con autenticazione.
    
    La documentazione delle API è disponibile qui:
    https://binance-docs.github.io/apidocs/spot/en/
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, currency: str = "USDT"):
        """
        Inizializza il wrapper con le credenziali API.
        
        Args:
            api_key: Chiave API di Binance (se None, usa variabile d'ambiente)
            api_secret: Secret API di Binance (se None, usa variabile d'ambiente)
            currency: Valuta di quotazione di default (default: USDT)
        """
        if api_key is None:
            api_key = os.getenv("BINANCE_API_KEY")
        assert api_key is not None, "API key is required"

        if api_secret is None:
            api_secret = os.getenv("BINANCE_API_SECRET")
        assert api_secret is not None, "API secret is required"

        self.currency = currency
        self.client = Client(api_key=api_key, api_secret=api_secret)

    def __format_symbol(self, asset_id: str) -> str:
        """
        Formatta l'asset_id nel formato richiesto da Binance.
        
        Args:
            asset_id: ID dell'asset (es. "BTC" o "BTC-USDT")
        
        Returns:
            Simbolo formattato per Binance (es. "BTCUSDT")
        """
        if '-' in asset_id:
            # Se già nel formato "BTC-USDT", converte in "BTCUSDT"
            return asset_id.replace('-', '')
        else:
            # Se solo "BTC", aggiunge la valuta di default
            return f"{asset_id}{self.currency}"

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_product(self, asset_id: str) -> ProductInfo:
        """
        Ottiene informazioni su un singolo prodotto.
        
        Args:
            asset_id: ID dell'asset da recuperare
        
        Returns:
            Oggetto ProductInfo con le informazioni del prodotto
        """
        symbol = self.__format_symbol(asset_id)
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        ticker_24h = self.client.get_ticker(symbol=symbol)
        
        return ProductInfo.from_binance(ticker, ticker_24h)

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        """
        Ottiene informazioni su più prodotti.
        
        Args:
            asset_ids: Lista di ID degli asset da recuperare
        
        Returns:
            Lista di oggetti ProductInfo
        """
        products = []
        for asset_id in asset_ids:
            try:
                product = self.get_product(asset_id)
                products.append(product)
            except Exception as e:
                print(f"Errore nel recupero di {asset_id}: {e}")
                continue
        return products

    @retry_on_failure(max_retries=3, delay=1.0)
    @handle_api_errors
    def get_all_products(self) -> list[ProductInfo]:
        """
        Ottiene informazioni su tutti i prodotti disponibili.
        
        Returns:
            Lista di oggetti ProductInfo per tutti i prodotti
        """
        try:
            # Ottiene tutti i ticker 24h che contengono le informazioni necessarie
            all_tickers = self.client.get_ticker()
            products = []
            
            for ticker in all_tickers:
                # Filtra solo i simboli che terminano con la valuta di default
                if ticker['symbol'].endswith(self.currency):
                    try:
                        # Crea ProductInfo direttamente dal ticker 24h
                        product = ProductInfo()
                        product.id = ticker['symbol']
                        product.symbol = ticker['symbol'].replace(self.currency, '')
                        product.price = float(ticker['lastPrice'])
                        product.volume_24h = float(ticker['volume'])
                        product.status = "TRADING"  # Binance non fornisce status esplicito
                        product.quote_currency = self.currency
                        products.append(product)
                    except (ValueError, KeyError) as e:
                        print(f"Errore nel parsing di {ticker['symbol']}: {e}")
                        continue
            
            return products
        except Exception as e:
            print(f"Errore nel recupero di tutti i prodotti: {e}")
            return []

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
            # Ottiene candele orarie degli ultimi 30 giorni
            klines = self.client.get_historical_klines(
                symbol=symbol,
                interval=Client.KLINE_INTERVAL_1HOUR,
                start_str="30 days ago UTC"
            )
            
            prices = []
            for kline in klines:
                price = Price()
                price.open = float(kline[1])
                price.high = float(kline[2])
                price.low = float(kline[3])
                price.close = float(kline[4])
                price.volume = float(kline[5])
                price.time = str(datetime.fromtimestamp(kline[0] / 1000))
                prices.append(price)
            
            return prices
        except Exception as e:
            print(f"Errore nel recupero dei prezzi storici per {symbol}: {e}")
            return []
