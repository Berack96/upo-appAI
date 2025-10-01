import statistics
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field, PrivateAttr
from app.markets.base import ProductInfo

class AggregationMetadata(BaseModel):
    """Metadati nascosti per debugging e audit trail"""
    sources_used: Set[str] = Field(default_factory=set, description="Exchange usati nell'aggregazione")
    sources_ignored: Set[str] = Field(default_factory=set, description="Exchange ignorati (errori)")
    aggregation_timestamp: str = Field(default="", description="Timestamp dell'aggregazione")
    confidence_score: float = Field(default=0.0, description="Score 0-1 sulla qualità dei dati")

    class Config:
        # Nasconde questi campi dalla serializzazione di default
        extra = "forbid"

class AggregatedProductInfo(ProductInfo):
    """
    Versione aggregata di ProductInfo che mantiene la trasparenza per l'utente finale
    mentre fornisce metadati di debugging opzionali.
    """

    # Override dei campi con logica di aggregazione
    id: str = Field(description="ID aggregato basato sul simbolo standardizzato")
    status: str = Field(description="Status aggregato (majority vote o conservative)")

    # Campi privati per debugging (non visibili di default)
    _metadata: Optional[AggregationMetadata] = PrivateAttr(default=None)
    _source_data: Optional[Dict[str, ProductInfo]] = PrivateAttr(default=None)

    @classmethod
    def from_multiple_sources(cls, products: List[ProductInfo]) -> 'AggregatedProductInfo':
        """
        Crea un AggregatedProductInfo da una lista di ProductInfo.
        Usa strategie intelligenti per gestire ID e status.
        """
        if not products:
            raise ValueError("Nessun prodotto da aggregare")

        # Raggruppa per symbol (la chiave vera per l'aggregazione)
        symbol_groups = {}
        for product in products:
            if product.symbol not in symbol_groups:
                symbol_groups[product.symbol] = []
            symbol_groups[product.symbol].append(product)

        # Per ora gestiamo un symbol alla volta
        if len(symbol_groups) > 1:
            raise ValueError(f"Simboli multipli non supportati: {list(symbol_groups.keys())}")

        symbol_products = list(symbol_groups.values())[0]

        # Estrai tutte le fonti
        sources = []
        for product in symbol_products:
            # Determina la fonte dall'ID o da altri metadati se disponibili
            source = cls._detect_source(product)
            sources.append(source)

        # Aggrega i dati
        aggregated_data = cls._aggregate_products(symbol_products, sources)

        # Crea l'istanza e assegna gli attributi privati
        instance = cls(**aggregated_data)
        instance._metadata = aggregated_data.get("_metadata")
        instance._source_data = aggregated_data.get("_source_data")

        return instance

    @staticmethod
    def _detect_source(product: ProductInfo) -> str:
        """Rileva la fonte da un ProductInfo"""
        # Strategia semplice: usa pattern negli ID
        if "coinbase" in product.id.lower() or "cb" in product.id.lower():
            return "coinbase"
        elif "binance" in product.id.lower() or "bn" in product.id.lower():
            return "binance"
        elif "crypto" in product.id.lower() or "cc" in product.id.lower():
            return "cryptocompare"
        elif "yfinance" in product.id.lower() or "yf" in product.id.lower():
            return "yfinance"
        else:
            return "unknown"

    @classmethod
    def _aggregate_products(cls, products: List[ProductInfo], sources: List[str]) -> dict:
        """
        Logica di aggregazione principale.
        Gestisce ID, status e altri campi numerici.
        """
        import statistics
        from datetime import datetime

        # ID: usa il symbol come chiave standardizzata
        symbol = products[0].symbol
        aggregated_id = f"{symbol}_AGG"

        # Status: strategia "conservativa" - il più restrittivo vince
        # Ordine: trading_only < limit_only < auction < maintenance < offline
        status_priority = {
            "trading": 1,
            "limit_only": 2, 
            "auction": 3,
            "maintenance": 4,
            "offline": 5,
            "": 0  # Default se non specificato
        }

        statuses = [p.status for p in products if p.status]
        if statuses:
            # Prendi lo status con priorità più alta (più restrittivo)
            aggregated_status = max(statuses, key=lambda s: status_priority.get(s, 0))
        else:
            aggregated_status = "trading"  # Default ottimistico

        # Prezzo: media semplice (uso diretto del campo price come float)
        prices = [p.price for p in products if p.price > 0]
        aggregated_price = statistics.mean(prices) if prices else 0.0

        # Volume: somma (assumendo che i volumi siano esclusivi per exchange)
        volumes = [p.volume_24h for p in products if p.volume_24h > 0]
        total_volume = sum(volumes)
        aggregated_volume = sum(price_i * volume_i for price_i, volume_i in zip((p.price for p in products), (volume for volume in volumes))) / total_volume
        aggregated_volume = round(aggregated_volume, 5)
        # aggregated_volume = sum(volumes) if volumes else 0.0 # NOTE old implementation

        # Valuta: prendi la prima (dovrebbero essere tutte uguali)
        quote_currency = next((p.quote_currency for p in products if p.quote_currency), "USD")

        # Calcola confidence score
        confidence = cls._calculate_confidence(products, sources)

        # Crea metadati per debugging
        metadata = AggregationMetadata(
            sources_used=set(sources),
            aggregation_timestamp=datetime.now().isoformat(),
            confidence_score=confidence
        )

        # Salva dati sorgente per debugging
        source_data = dict(zip(sources, products))

        return {
            "symbol": symbol,
            "price": aggregated_price,
            "volume_24h": aggregated_volume,
            "quote_currency": quote_currency,
            "id": aggregated_id,
            "status": aggregated_status,
            "_metadata": metadata,
            "_source_data": source_data
        }

    @staticmethod
    def _calculate_confidence(products: List[ProductInfo], sources: List[str]) -> float:
        """Calcola un punteggio di confidenza 0-1"""
        if not products:
            return 0.0

        score = 1.0

        # Riduci score se pochi dati
        if len(products) < 2:
            score *= 0.7

        # Riduci score se prezzi troppo diversi
        prices = [p.price for p in products if p.price > 0]
        if len(prices) > 1:
            price_std = (max(prices) - min(prices)) / statistics.mean(prices)
            if price_std > 0.05:  # >5% variazione
                score *= 0.8

        # Riduci score se fonti sconosciute
        unknown_sources = sum(1 for s in sources if s == "unknown")
        if unknown_sources > 0:
            score *= (1 - unknown_sources / len(sources))

        return max(0.0, min(1.0, score))

    def get_debug_info(self) -> dict:
        """Metodo opzionale per ottenere informazioni di debug"""
        return {
            "aggregated_product": self.dict(),
            "metadata": self._metadata.dict() if self._metadata else None,
            "sources": list(self._source_data.keys()) if self._source_data else []
        }