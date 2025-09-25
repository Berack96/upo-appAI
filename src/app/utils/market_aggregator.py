import statistics
from typing import Dict, List, Any

class MarketAggregator:
    """
    Aggrega dati di mercato da più provider e genera segnali e analisi avanzate.
    """
    @staticmethod
    def aggregate(symbol: str, sources: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        prices = []
        volumes = []
        price_map = {}
        for provider, data in sources.items():
            price = data.get('price')
            if price is not None:
                prices.append(price)
                price_map[provider] = price
            volume = data.get('volume')
            if volume is not None:
                volumes.append(MarketAggregator._parse_volume(volume))
        
        # Aggregated price (mean)
        agg_price = statistics.mean(prices) if prices else None
        # Spread analysis
        spread = (max(prices) - min(prices)) / agg_price if prices and agg_price else 0
        # Confidence
        stddev = statistics.stdev(prices) if len(prices) > 1 else 0
        confidence = max(0.5, 1 - (stddev / agg_price)) if agg_price else 0
        if spread < 0.005:
            confidence += 0.1
        if len(prices) >= 3:
            confidence += 0.05
        confidence = min(confidence, 1.0)
        # Volume trend
        total_volume = sum(volumes) if volumes else None
        # Price divergence
        max_deviation = (max(prices) - min(prices)) / agg_price if prices and agg_price else 0
        # Signals
        signals = {
            "spread_analysis": f"Low spread ({spread:.2%}) indicates healthy liquidity" if spread < 0.01 else f"Spread {spread:.2%} - check liquidity",
            "volume_trend": f"Combined volume: {total_volume:.2f}" if total_volume else "Volume data not available",
            "price_divergence": f"Max deviation: {max_deviation:.2%} - {'Normal range' if max_deviation < 0.01 else 'High divergence'}"
        }
        return {
            "aggregated_data": {
                f"{symbol}_USD": {
                    "price": round(agg_price, 2) if agg_price else None,
                    "confidence": round(confidence, 2),
                    "sources_count": len(prices)
                }
            },
            "individual_sources": price_map,
            "market_signals": signals
        }
    @staticmethod
    def _parse_volume(volume: Any) -> float:
        # Supporta stringhe tipo "1.2M" o numeri
        if isinstance(volume, (int, float)):
            return float(volume)
        if isinstance(volume, str):
            v = volume.upper().replace(' ', '')
            if v.endswith('M'):
                return float(v[:-1]) * 1_000_000
            if v.endswith('K'):
                return float(v[:-1]) * 1_000
            try:
                return float(v)
            except Exception:
                return 0.0
        return 0.0
