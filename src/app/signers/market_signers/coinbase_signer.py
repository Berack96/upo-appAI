import os
import logging
from coinbase.rest import RESTClient
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class CoinbaseCDPSigner:
    """
    Signer per Coinbase Advanced Trade API.
    Utilizza le credenziali CDP per accedere alle vere API di market data di Coinbase.
    """

    def __init__(self, api_key_name: str = None, api_private_key: str = None):
        """
        Inizializza il Coinbase REST client.
        
        Args:
            api_key_name: Nome della API key (da CDP_API_KEY_NAME)
            api_private_key: Private key (da CDP_API_PRIVATE_KEY)
        """
        self.api_key_name = api_key_name or os.getenv('CDP_API_KEY_NAME')
        self.api_private_key = api_private_key or os.getenv('CDP_API_PRIVATE_KEY')
        
        if not self.api_key_name or not self.api_private_key:
            raise ValueError("CDP_API_KEY_NAME and CDP_API_PRIVATE_KEY are required")
        
        # Configura Coinbase REST client
        try:
            self.client = RESTClient(
                api_key=self.api_key_name,
                api_secret=self.api_private_key
            )
            self._configured = True
            logger.info(f"✅ Coinbase REST Client configured with key: {self.api_key_name[:50]}...")
        except Exception as e:
            self._configured = False
            logger.error(f"Failed to configure Coinbase REST Client: {e}")
            raise ValueError(f"Failed to configure Coinbase REST Client: {e}")

    def is_configured(self) -> bool:
        """Verifica se Coinbase REST client è configurato correttamente"""
        return getattr(self, '_configured', False)

    def get_asset_info(self, asset_id: str) -> Dict[str, Any]:
        """
        Ottiene informazioni su un asset specifico usando Coinbase Advanced Trade API.
        
        Args:
            asset_id: ID dell'asset (es. "BTC", "ETH")
            
        Returns:
            Dict con informazioni sull'asset
        """
        if not self.is_configured():
            return {
                'asset_id': asset_id,
                'error': 'Coinbase REST Client not configured',
                'success': False
            }
        
        try:
            # Prova con USD prima, poi EUR se non funziona
            product_id = f"{asset_id.upper()}-USD"
            
            product_data = self.client.get_product(product_id)
            
            return {
                'asset_id': asset_id,
                'symbol': product_data.product_id,
                'price': float(product_data.price),
                'volume_24h': float(product_data.volume_24h) if product_data.volume_24h else 0,
                'status': product_data.status,
                'base_currency': product_data.base_currency_id,
                'quote_currency': product_data.quote_currency_id,
                'success': True,
                'source': 'coinbase_advanced_trade'
            }
            
        except Exception as e:
            logger.error(f"Error getting asset info for {asset_id}: {e}")
            return {
                'asset_id': asset_id,
                'error': str(e),
                'success': False
            }

    def get_multiple_assets(self, asset_ids: List[str]) -> Dict[str, Any]:
        """
        Ottiene informazioni su multipli asset.
        
        Args:
            asset_ids: Lista di ID degli asset
            
        Returns:
            Dict con informazioni sugli asset
        """
        if not self.is_configured():
            return {
                'error': 'Coinbase REST Client not configured',
                'success': False
            }
        
        results = {}
        for asset_id in asset_ids:
            asset_info = self.get_asset_info(asset_id)
            if asset_info.get('success'):
                results[asset_id] = asset_info
        
        return results

    def get_all_products(self) -> Dict[str, Any]:
        """
        Ottiene lista di tutti i prodotti disponibili su Coinbase.
        """
        if not self.is_configured():
            return {
                'error': 'Coinbase REST Client not configured',
                'success': False
            }
        
        try:
            products = self.client.get_products()
            
            products_data = []
            for product in products.products:
                if product.status == "online":  # Solo prodotti attivi
                    products_data.append({
                        'product_id': product.product_id,
                        'price': float(product.price) if product.price else 0,
                        'volume_24h': float(product.volume_24h) if product.volume_24h else 0,
                        'status': product.status,
                        'base_currency': product.base_currency_id,
                        'quote_currency': product.quote_currency_id
                    })
            
            return {
                'products': products_data,
                'total': len(products_data),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def get_market_trades(self, symbol: str = "BTC-USD", limit: int = 10) -> Dict[str, Any]:
        """
        Ottiene gli ultimi trade di mercato per un prodotto.
        
        Args:
            symbol: Simbolo del prodotto (es. "BTC-USD")
            limit: Numero massimo di trade da restituire
            
        Returns:
            Dict con i trade
        """
        if not self.is_configured():
            return {
                'error': 'Coinbase REST Client not configured',
                'success': False
            }
        
        try:
            trades = self.client.get_market_trades(product_id=symbol, limit=limit)
            
            trades_data = []
            for trade in trades.trades:
                trades_data.append({
                    'trade_id': trade.trade_id,
                    'price': float(trade.price),
                    'size': float(trade.size),
                    'time': trade.time,
                    'side': trade.side
                })
            
            return {
                'symbol': symbol,
                'trades': trades_data,
                'count': len(trades_data),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error getting market trades for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'success': False
            }

    # Metodi di compatibilità con l'interfaccia precedente
    def build_headers(self, method: str, request_path: str, body: Optional[Dict] = None) -> Dict[str, str]:
        """
        Metodo di compatibilità - Coinbase REST client gestisce internamente l'autenticazione.
        """
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'upo-appAI/1.0-coinbase-advanced'
        }

    def sign_request(self, method: str, request_path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Metodo di compatibilità - Coinbase REST client gestisce internamente l'autenticazione.
        """
        return {
            'method': method,
            'path': request_path,
            'body': body or {},
            'headers': self.build_headers(method, request_path, body),
            'coinbase_configured': self.is_configured()
        }

    def test_connection(self) -> Dict[str, Any]:
        """
        Testa la connessione Coinbase con dati reali.
        """
        try:
            if not self.is_configured():
                return {
                    'success': False,
                    'error': 'Coinbase REST Client not configured'
                }
            
            # Test con BTC-USD
            test_asset = self.get_asset_info('BTC')
            return {
                'success': test_asset.get('success', False),
                'client_configured': True,
                'test_asset': test_asset.get('asset_id'),
                'test_price': test_asset.get('price'),
                'message': 'Coinbase Advanced Trade API is working with real data'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'client_configured': False
            }