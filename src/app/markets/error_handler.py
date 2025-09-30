"""
Modulo per la gestione robusta degli errori nei market providers.

Fornisce decoratori e utilità per:
- Retry automatico con backoff esponenziale
- Logging standardizzato degli errori
- Gestione di timeout e rate limiting
- Fallback tra provider multipli
"""

import time
import logging
from functools import wraps
from typing import Any, Callable, Optional, Type, Union, List
from requests.exceptions import RequestException, Timeout, ConnectionError
from binance.exceptions import BinanceAPIException, BinanceRequestException
from .base import ProductInfo

# Configurazione logging
logger = logging.getLogger(__name__)

class MarketAPIError(Exception):
    """Eccezione base per errori delle API di mercato."""
    pass

class RateLimitError(MarketAPIError):
    """Eccezione per errori di rate limiting."""
    pass

class AuthenticationError(MarketAPIError):
    """Eccezione per errori di autenticazione."""
    pass

class DataNotFoundError(MarketAPIError):
    """Eccezione quando i dati richiesti non sono disponibili."""
    pass

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (RequestException, BinanceAPIException, BinanceRequestException)
) -> Callable:
    """
    Decoratore per retry automatico con backoff esponenziale.
    
    Args:
        max_retries: Numero massimo di tentativi
        delay: Delay iniziale in secondi
        backoff_factor: Fattore di moltiplicazione per il delay
        exceptions: Tuple di eccezioni da catturare per il retry
    
    Returns:
        Decoratore per la funzione
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries + 1} attempts. "
                            f"Last error: {str(e)}"
                        )
                        raise MarketAPIError(f"Max retries exceeded: {str(e)}") from e
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
                except Exception as e:
                    # Per eccezioni non previste, non fare retry
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                    raise
            
            # Questo non dovrebbe mai essere raggiunto
            if last_exception:
                raise last_exception
            else:
                raise MarketAPIError("Unknown error occurred")
        
        return wrapper
    return decorator

def handle_api_errors(func: Callable) -> Callable:
    """
    Decoratore per gestione standardizzata degli errori API.
    
    Converte errori specifici dei provider in eccezioni standardizzate.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except BinanceAPIException as e:
            if e.code == -1021:  # Timestamp error
                raise MarketAPIError(f"Binance timestamp error: {e.message}")
            elif e.code == -1003:  # Rate limit
                raise RateLimitError(f"Binance rate limit exceeded: {e.message}")
            elif e.code in [-2014, -2015]:  # API key errors
                raise AuthenticationError(f"Binance authentication error: {e.message}")
            else:
                raise MarketAPIError(f"Binance API error [{e.code}]: {e.message}")
        except ConnectionError as e:
            raise MarketAPIError(f"Connection error: {str(e)}")
        except Timeout as e:
            raise MarketAPIError(f"Request timeout: {str(e)}")
        except RequestException as e:
            raise MarketAPIError(f"Request error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise MarketAPIError(f"Unexpected error: {str(e)}") from e
    
    return wrapper

def safe_execute(
    func: Callable,
    default_value: Any = None,
    log_errors: bool = True,
    error_message: Optional[str] = None
) -> Any:
    """
    Esegue una funzione in modo sicuro, restituendo un valore di default in caso di errore.
    
    Args:
        func: Funzione da eseguire
        default_value: Valore da restituire in caso di errore
        log_errors: Se loggare gli errori
        error_message: Messaggio di errore personalizzato
    
    Returns:
        Risultato della funzione o valore di default
    """
    try:
        return func()
    except Exception as e:
        if log_errors:
            message = error_message or f"Error executing {func.__name__}"
            logger.warning(f"{message}: {str(e)}")
        return default_value

class ProviderFallback:
    """
    Classe per gestire il fallback tra provider multipli.
    """
    
    def __init__(self, providers: List[Any]):
        """
        Inizializza con una lista di provider ordinati per priorità.
        
        Args:
            providers: Lista di provider ordinati per priorità
        """
        self.providers = providers
    
    def execute_with_fallback(
        self,
        method_name: str,
        *args,
        **kwargs
    ) -> list[ProductInfo]:
        """
        Esegue un metodo su tutti i provider fino a trovarne uno che funziona.
        
        Args:
            method_name: Nome del metodo da chiamare
            *args: Argomenti posizionali
            **kwargs: Argomenti nominali
        
        Returns:
            Risultato del primo provider che funziona
        
        Raises:
            MarketAPIError: Se tutti i provider falliscono
        """
        last_error = None
        
        for i, provider in enumerate(self.providers):
            try:
                if hasattr(provider, method_name):
                    method = getattr(provider, method_name)
                    result = method(*args, **kwargs)
                    
                    if i > 0:  # Se non è il primo provider
                        logger.info(f"Fallback successful: used provider {type(provider).__name__}")
                    
                    return result
                else:
                    logger.warning(f"Provider {type(provider).__name__} doesn't have method {method_name}")
                    continue
                    
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Provider {type(provider).__name__} failed for {method_name}: {str(e)}"
                )
                continue
        
        # Se arriviamo qui, tutti i provider hanno fallito
        raise MarketAPIError(
            f"All providers failed for method {method_name}. Last error: {str(last_error)}"
        )

def validate_response_data(data: Any, required_fields: Optional[List[str]] = None) -> bool:
    """
    Valida che i dati di risposta contengano i campi richiesti.
    
    Args:
        data: Dati da validare
        required_fields: Lista di campi richiesti
    
    Returns:
        True se i dati sono validi, False altrimenti
    """
    if data is None:
        return False
    
    if required_fields is None:
        return True
    
    if isinstance(data, dict):
        return all(field in data for field in required_fields)
    elif hasattr(data, '__dict__'):
        return all(hasattr(data, field) for field in required_fields)
    
    return False