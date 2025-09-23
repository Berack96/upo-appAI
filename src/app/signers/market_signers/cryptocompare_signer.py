import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode


class CryptoCompareSigner:
    """Genera le intestazioni e parametri di autenticazione per CryptoCompare API.
    
    CryptoCompare utilizza un'autenticazione semplice basata su API key che può essere
    passata come parametro nella query string o nell'header Authorization.
    
    Contratto:
    - Input: api_key, metodo di autenticazione (query o header)
    - Output: dict di header e parametri per la richiesta
    - Errori: solleva ValueError se api_key non è fornita
    """

    def __init__(self, api_key: str, auth_method: str = "query") -> None:
        """
        Inizializza il signer per CryptoCompare.
        
        Args:
            api_key: La chiave API di CryptoCompare
            auth_method: Metodo di autenticazione ("query" o "header")
                        - "query": aggiunge api_key come parametro URL
                        - "header": aggiunge api_key nell'header Authorization
        """
        if not api_key:
            raise ValueError("API key è richiesta per CryptoCompare")
            
        self.api_key = api_key
        self.auth_method = auth_method.lower()
        
        if self.auth_method not in ("query", "header"):
            raise ValueError("auth_method deve essere 'query' o 'header'")

    def build_headers(self, include_timestamp: bool = False) -> Dict[str, str]:
        """
        Costruisce gli header per la richiesta CryptoCompare.
        
        Args:
            include_timestamp: Se includere un timestamp nell'header (opzionale)
            
        Returns:
            Dict con gli header necessari
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "upo-appAI/1.0"
        }
        
        # Se si usa autenticazione via header
        if self.auth_method == "header":
            headers["Authorization"] = f"Apikey {self.api_key}"
        
        # Aggiungi timestamp se richiesto (utile per debugging)
        if include_timestamp:
            headers["X-Request-Timestamp"] = str(int(time.time()))
            
        return headers

    def build_url_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Costruisce i parametri URL includendo l'API key se necessario.
        
        Args:
            params: Parametri aggiuntivi per la query
            
        Returns:
            Dict con tutti i parametri per l'URL
        """
        if params is None:
            params = {}
            
        # Se si usa autenticazione via query string
        if self.auth_method == "query":
            params["api_key"] = self.api_key
            
        return params

    def build_full_url(self, base_url: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Costruisce l'URL completo con tutti i parametri.
        
        Args:
            base_url: URL base dell'API (es. "https://min-api.cryptocompare.com")
            endpoint: Endpoint specifico (es. "/data/pricemulti")
            params: Parametri aggiuntivi per la query
            
        Returns:
            URL completo con parametri
        """
        base_url = base_url.rstrip("/")
        endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        
        url_params = self.build_url_params(params)
        
        if url_params:
            query_string = urlencode(url_params)
            return f"{base_url}{endpoint}?{query_string}"
        else:
            return f"{base_url}{endpoint}"

    def prepare_request(self, 
                       base_url: str, 
                       endpoint: str, 
                       params: Optional[Dict[str, Any]] = None,
                       include_timestamp: bool = False) -> Dict[str, Any]:
        """
        Prepara tutti i componenti per una richiesta CryptoCompare.
        
        Args:
            base_url: URL base dell'API
            endpoint: Endpoint specifico
            params: Parametri per la query
            include_timestamp: Se includere timestamp negli header
            
        Returns:
            Dict con url, headers e params pronti per la richiesta
        """
        return {
            "url": self.build_full_url(base_url, endpoint, params),
            "headers": self.build_headers(include_timestamp),
            "params": self.build_url_params(params) if self.auth_method == "query" else params or {}
        }

    # Alias per compatibilità con il pattern Coinbase
    def sign_request(self, 
                    endpoint: str, 
                    params: Optional[Dict[str, Any]] = None,
                    base_url: str = "https://min-api.cryptocompare.com") -> Dict[str, Any]:
        """
        Alias per prepare_request per mantenere compatibilità con il pattern del CoinbaseSigner.
        """
        return self.prepare_request(base_url, endpoint, params)