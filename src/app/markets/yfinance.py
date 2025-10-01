import json
from agno.tools.yfinance import YFinanceTools
from .base import BaseWrapper, ProductInfo, Price


def create_product_info(symbol: str, stock_data: dict) -> ProductInfo:
    """
    Converte i dati di YFinanceTools in ProductInfo.
    """
    product = ProductInfo()
    
    # ID univoco per yfinance
    product.id = f"yfinance_{symbol}"
    product.symbol = symbol
    
    # Estrai il prezzo corrente - gestisci diversi formati
    if 'currentPrice' in stock_data:
        product.price = float(stock_data['currentPrice'])
    elif 'regularMarketPrice' in stock_data:
        product.price = float(stock_data['regularMarketPrice'])
    elif 'Current Stock Price' in stock_data:
        # Formato: "254.63 USD" - estrai solo il numero
        price_str = stock_data['Current Stock Price'].split()[0]
        try:
            product.price = float(price_str)
        except ValueError:
            product.price = 0.0
    else:
        product.price = 0.0
    
    # Volume 24h
    if 'volume' in stock_data:
        product.volume_24h = float(stock_data['volume'])
    elif 'regularMarketVolume' in stock_data:
        product.volume_24h = float(stock_data['regularMarketVolume'])
    else:
        product.volume_24h = 0.0
    
    # Status basato sulla disponibilità dei dati
    product.status = "trading" if product.price > 0 else "offline"
    
    # Valuta (default USD)
    product.quote_currency = stock_data.get('currency', 'USD') or 'USD'
    
    return product


def create_price_from_history(hist_data: dict, timestamp: str) -> Price:
    """
    Converte i dati storici di YFinanceTools in Price.
    """
    price = Price()
    
    if timestamp in hist_data:
        day_data = hist_data[timestamp]
        price.high = float(day_data.get('High', 0.0))
        price.low = float(day_data.get('Low', 0.0))
        price.open = float(day_data.get('Open', 0.0))
        price.close = float(day_data.get('Close', 0.0))
        price.volume = float(day_data.get('Volume', 0.0))
        price.time = timestamp
    
    return price


class YFinanceWrapper(BaseWrapper):
    """
    Wrapper per YFinanceTools che fornisce dati di mercato per azioni, ETF e criptovalute.
    Implementa l'interfaccia BaseWrapper per compatibilità con il sistema esistente.
    Usa YFinanceTools dalla libreria agno per coerenza con altri wrapper.
    """
    
    def __init__(self, currency: str = "USD"):
        self.currency = currency
        # Inizializza YFinanceTools - non richiede parametri specifici
        self.tool = YFinanceTools()
    
    def _format_symbol(self, asset_id: str) -> str:
        """
        Formatta il simbolo per yfinance.
        Per crypto, aggiunge '-USD' se non presente.
        """
        asset_id = asset_id.upper()
        
        # Se è già nel formato corretto (es: BTC-USD), usa così
        if '-' in asset_id:
            return asset_id
        
        # Per crypto singole (BTC, ETH), aggiungi -USD
        if asset_id in ['BTC', 'ETH', 'ADA', 'SOL', 'DOT', 'LINK', 'UNI', 'AAVE']:
            return f"{asset_id}-USD"
        
        # Per azioni, usa il simbolo così com'è
        return asset_id
    
    def get_product(self, asset_id: str) -> ProductInfo:
        """
        Recupera le informazioni di un singolo prodotto.
        """
        symbol = self._format_symbol(asset_id)
        
        # Usa YFinanceTools per ottenere i dati
        try:
            # Ottieni le informazioni base dello stock
            stock_info = self.tool.get_company_info(symbol)
            
            # Se il risultato è una stringa JSON, parsala
            if isinstance(stock_info, str):
                try:
                    stock_data = json.loads(stock_info)
                except json.JSONDecodeError:
                    # Se non è JSON valido, prova a ottenere solo il prezzo
                    price_data_str = self.tool.get_current_stock_price(symbol)
                    if price_data_str and price_data_str.replace('.', '').replace('-', '').isdigit():
                        price = float(price_data_str)
                        stock_data = {'currentPrice': price, 'currency': 'USD'}
                    else:
                        raise Exception("Dati non validi")
            else:
                stock_data = stock_info
            
            return create_product_info(symbol, stock_data)
            
        except Exception as e:
            # Fallback: prova a ottenere solo il prezzo
            try:
                price_data_str = self.tool.get_current_stock_price(symbol)
                if price_data_str and price_data_str.replace('.', '').replace('-', '').isdigit():
                    price = float(price_data_str)
                    minimal_data = {
                        'currentPrice': price,
                        'currency': 'USD'
                    }
                    return create_product_info(symbol, minimal_data)
                else:
                    raise Exception("Prezzo non disponibile")
            except Exception:
                # Se tutto fallisce, restituisci un prodotto vuoto
                product = ProductInfo()
                product.symbol = symbol
                product.status = "offline"
                return product
    
    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        """
        Recupera le informazioni di multiple assets.
        """
        products = []
        
        for asset_id in asset_ids:
            try:
                product = self.get_product(asset_id)
                products.append(product)
            except Exception as e:
                # Se un asset non è disponibile, continua con gli altri
                continue
        
        return products
    
    def get_all_products(self) -> list[ProductInfo]:
        """
        Recupera tutti i prodotti disponibili.
        Restituisce una lista predefinita di asset popolari.
        """
        # Lista di asset popolari (azioni, ETF, crypto)
        popular_assets = [
            'BTC', 'ETH', 'ADA', 'SOL', 'DOT',
            'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN',
            'SPY', 'QQQ', 'VTI', 'GLD', 'VIX'
        ]
        
        return self.get_products(popular_assets)
    
    def get_historical_prices(self, asset_id: str = "BTC", limit: int = 100) -> list[Price]:
        """
        Recupera i dati storici di prezzo per un asset.
        """
        symbol = self._format_symbol(asset_id)
        
        try:
            # Determina il periodo appropriato in base al limite
            if limit <= 7:
                period = "1d"
                interval = "15m"
            elif limit <= 30:
                period = "5d"
                interval = "1h"
            elif limit <= 90:
                period = "1mo"
                interval = "1d"
            else:
                period = "3mo"
                interval = "1d"
            
            # Ottieni i dati storici
            hist_data = self.tool.get_historical_stock_prices(symbol, period=period, interval=interval)
            
            if isinstance(hist_data, str):
                hist_data = json.loads(hist_data)
            
            # Il formato dei dati è {timestamp: {Open: x, High: y, Low: z, Close: w, Volume: v}}
            prices = []
            timestamps = sorted(hist_data.keys())[-limit:]  # Prendi gli ultimi 'limit' timestamp
            
            for timestamp in timestamps:
                price = create_price_from_history(hist_data, timestamp)
                if price.close > 0:  # Solo se ci sono dati validi
                    prices.append(price)
            
            return prices
            
        except Exception as e:
            # Se fallisce, restituisci lista vuota
            return []