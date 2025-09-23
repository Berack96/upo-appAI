import base64
import hashlib
import hmac
import json
import time
from typing import Any, Mapping, Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization


class CoinbaseSigner:
    """
    Genera le intestazioni di autenticazione per Coinbase Advanced Trade API.
    
    Supporta due formati di autenticazione:
    1. Legacy: API key, secret (base64), passphrase (per retrocompatibilità)
    2. New: API key name, private key (nuovo formato Coinbase)
    
    Contratto:
    - Input: method, request_path, body opzionale, timestamp opzionale
    - Output: dict di header richiesti dall'API
    - Errori: solleva eccezioni se le credenziali non sono valide
    """

    def __init__(self, api_key: str, secret_or_private_key: str, passphrase: str = None) -> None:
        self.api_key = api_key
        self.passphrase = passphrase
        
        # Determina se stiamo usando il nuovo formato o il legacy
        if passphrase is None:
            # Nuovo formato: solo API key + private key
            self.auth_method = "new"
            self.private_key = self._load_private_key(secret_or_private_key)
            self.secret_b64 = None
        else:
            # Formato legacy: API key + secret + passphrase
            self.auth_method = "legacy"
            self.secret_b64 = secret_or_private_key
            self.private_key = None

    def _load_private_key(self, private_key_str: str):
        """Carica la private key dal formato PEM"""
        try:
            # Rimuovi eventuali spazi e aggiungi header/footer se mancanti
            key_str = private_key_str.strip()
            if not key_str.startswith("-----BEGIN"):
                key_str = f"-----BEGIN EC PRIVATE KEY-----\n{key_str}\n-----END EC PRIVATE KEY-----"
            
            private_key = serialization.load_pem_private_key(
                key_str.encode('utf-8'),
                password=None,
            )
            return private_key
        except Exception as e:
            raise ValueError(f"Invalid private key format: {e}")

    @staticmethod
    def _normalize_path(path: str) -> str:
        if not path:
            return "/"
        return path if path.startswith("/") else f"/{path}"

    def _build_legacy_headers(
        self,
        method: str,
        request_path: str,
        body: Optional[Mapping[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> dict:
        """Costruisce header usando il formato legacy (HMAC)"""
        # Timestamp in secondi come stringa
        ts = timestamp or str(int(time.time()))
        m = method.upper()
        req_path = self._normalize_path(request_path)

        # Il body deve essere stringa vuota per GET/DELETE o quando assente
        if body is None or m in ("GET", "DELETE"):
            body_str = ""
        else:
            # JSON deterministico, senza spazi
            body_str = json.dumps(body, separators=(",", ":"), ensure_ascii=False)

        # Concatenazione: timestamp + method + request_path + body
        message = f"{ts}{m}{req_path}{body_str}"

        # Decodifica secret (base64) e firma HMAC-SHA256
        key = base64.b64decode(self.secret_b64)
        signature = hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()
        cb_access_sign = base64.b64encode(signature).decode("utf-8")

        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": cb_access_sign,
            "CB-ACCESS-TIMESTAMP": ts,
            "CB-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
        }

    def _build_new_headers(
        self,
        method: str,
        request_path: str,
        body: Optional[Mapping[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> dict:
        """Costruisce header usando il nuovo formato (EC signature)"""
        # Timestamp in secondi come stringa  
        ts = timestamp or str(int(time.time()))
        m = method.upper()
        req_path = self._normalize_path(request_path)

        # Il body deve essere stringa vuota per GET/DELETE o quando assente
        if body is None or m in ("GET", "DELETE"):
            body_str = ""
        else:
            # JSON deterministico, senza spazi
            body_str = json.dumps(body, separators=(",", ":"), ensure_ascii=False)

        # Concatenazione: timestamp + method + request_path + body
        message = f"{ts}{m}{req_path}{body_str}"

        # Firma con ECDSA
        signature = self.private_key.sign(
            message.encode("utf-8"),
            ec.ECDSA(hashes.SHA256())
        )
        
        # Converti signature in base64
        cb_access_sign = base64.b64encode(signature).decode("utf-8")

        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": cb_access_sign,
            "CB-ACCESS-TIMESTAMP": ts,
            "Content-Type": "application/json",
        }

    def build_headers(
        self,
        method: str,
        request_path: str,
        body: Optional[Mapping[str, Any]] = None,
        timestamp: Optional[str] = None,
    ) -> dict:
        """Costruisce gli header di autenticazione usando il metodo appropriato"""
        if self.auth_method == "legacy":
            return self._build_legacy_headers(method, request_path, body, timestamp)
        else:
            return self._build_new_headers(method, request_path, body, timestamp)

    def sign_request(
        self,
        method: str,
        request_path: str,
        body: Optional[Mapping[str, Any]] = None,
        passphrase: Optional[str] = None,
    ) -> dict:
        return self.build_headers(method, request_path, body)
