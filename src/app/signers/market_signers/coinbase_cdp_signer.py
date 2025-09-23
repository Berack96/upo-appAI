import os
import logging
from cdp import *
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class CoinbaseCDPSigner:
    """
    Signer per Coinbase Developer Platform (CDP) SDK.
    Utilizza il nuovo sistema di autenticazione di Coinbase basato su CDP.
    """

    def __init__(self, api_key_name: str = None, api_private_key: str = None):
        """
        Inizializza il CDP signer.
        
        Args:
            api_key_name: Nome della API key (formato: organizations/org-id/apiKeys/key-id)
            api_private_key: Private key in formato PEM
        """
        self.api_key_name = api_key_name or os.getenv('CDP_API_KEY_NAME')
        self.api_private_key = api_private_key or os.getenv('CDP_API_PRIVATE_KEY')
        
        if not self.api_key_name or not self.api_private_key:
            raise ValueError("CDP_API_KEY_NAME and CDP_API_PRIVATE_KEY are required")
        
        # Configura CDP client
        try:
            self.client = CdpClient(
                api_key_id=self.api_key_name,
                api_key_secret=self.api_private_key,
                debugging=False
            )
            self._configured = True
            logger.info(f"✅ CDP Client configured with key: {self.api_key_name[:50]}...")
        except Exception as e:
            self._configured = False
            logger.error(f"Failed to configure CDP Client: {e}")
            raise ValueError(f"Failed to configure CDP SDK: {e}")

    def is_configured(self) -> bool:
        """Verifica se CDP è configurato correttamente"""
        return getattr(self, '_configured', False)

    def get_asset_info(self, asset_id: str) -> Dict[str, Any]:
        """
        Ottiene informazioni su un asset specifico.
        
        Args:
            asset_id: ID dell'asset (es. "BTC", "ETH")
            
        Returns:
            Dict con informazioni sull'asset
        """
        if not self.is_configured():
            return {
                'asset_id': asset_id,
                'error': 'CDP Client not configured',
                'success': False
            }
        
        try:
            # Per ora, restituiamo un mock data structure
            # In futuro, quando CDP avrà metodi per asset info, useremo quelli
            return {
                'asset_id': asset_id,
                'price': self._get_mock_price(asset_id),
                'symbol': asset_id,
                'name': self._get_asset_name(asset_id),
                'success': True,
                'source': 'cdp_mock'
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
                'error': 'CDP Client not configured',
                'success': False
            }
        
        results = {}
        for asset_id in asset_ids:
            asset_info = self.get_asset_info(asset_id)
            if asset_info.get('success'):
                results[asset_id] = asset_info
        
        return results

    def _get_mock_price(self, asset_id: str) -> float:
        """
        Mock prices per i test - da sostituire con vere API CDP quando disponibili
        """
        mock_prices = {
            'BTC': 63500.0,
            'ETH': 2650.0,
            'ADA': 0.45,
            'DOT': 5.2,
            'SOL': 145.0,
            'MATIC': 0.85,
            'LINK': 11.2,
            'UNI': 7.8
        }
        return mock_prices.get(asset_id.upper(), 100.0)

    def _get_asset_name(self, asset_id: str) -> str:
        """
        Mock asset names
        """
        names = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'ADA': 'Cardano',
            'DOT': 'Polkadot',
            'SOL': 'Solana',
            'MATIC': 'Polygon',
            'LINK': 'Chainlink',
            'UNI': 'Uniswap'
        }
        return names.get(asset_id.upper(), f"{asset_id} Token")

    # Metodi di compatibilità con l'interfaccia precedente
    def build_headers(self, method: str, request_path: str, body: Optional[Dict] = None) -> Dict[str, str]:
        """
        Metodo di compatibilità - CDP SDK gestisce internamente l'autenticazione.
        Restituisce headers basic.
        """
        return {
            'Content-Type': 'application/json',
            'User-Agent': 'upo-appAI/1.0-cdp'
        }

    def sign_request(self, method: str, request_path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Metodo di compatibilità - CDP SDK gestisce internamente l'autenticazione.
        """
        return {
            'method': method,
            'path': request_path,
            'body': body or {},
            'headers': self.build_headers(method, request_path, body),
            'cdp_configured': self.is_configured()
        }

    def test_connection(self) -> Dict[str, Any]:
        """
        Testa la connessione CDP
        """
        try:
            if not self.is_configured():
                return {
                    'success': False,
                    'error': 'CDP Client not configured'
                }
            
            # Test basic con mock data
            test_asset = self.get_asset_info('BTC')
            return {
                'success': test_asset.get('success', False),
                'client_configured': True,
                'test_asset': test_asset.get('asset_id'),
                'message': 'CDP Client is working with mock data'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'client_configured': False
            }