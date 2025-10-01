import pytest

from app.utils.market_data_aggregator import MarketDataAggregator
from app.utils.aggregated_models import AggregatedProductInfo
from app.markets.base import ProductInfo, Price


class TestMarketDataAggregator:
    
    def test_initialization(self):
        """Test che il MarketDataAggregator si inizializzi correttamente"""
        aggregator = MarketDataAggregator()
        assert aggregator is not None
        assert aggregator.is_aggregation_enabled() == True
        
    def test_aggregation_toggle(self):
        """Test del toggle dell'aggregazione"""
        aggregator = MarketDataAggregator()
        
        # Disabilita aggregazione
        aggregator.enable_aggregation(False)
        assert aggregator.is_aggregation_enabled() == False
        
        # Riabilita aggregazione
        aggregator.enable_aggregation(True)
        assert aggregator.is_aggregation_enabled() == True
        
    def test_aggregated_product_info_creation(self):
        """Test creazione AggregatedProductInfo da fonti multiple"""
        
        # Crea dati di esempio
        product1 = ProductInfo(
            id="BTC-USD",
            symbol="BTC-USD",
            price=50000.0,
            volume_24h=1000.0,
            status="active",
            quote_currency="USD"
        )
        
        product2 = ProductInfo(
            id="BTC-USD",
            symbol="BTC-USD", 
            price=50100.0,
            volume_24h=1100.0,
            status="active",
            quote_currency="USD"
        )
        
        # Aggrega i prodotti
        aggregated = AggregatedProductInfo.from_multiple_sources([product1, product2])
        
        assert aggregated.symbol == "BTC-USD"
        assert aggregated.price == pytest.approx(50050.0, rel=1e-3)  # media tra 50000 e 50100
        assert aggregated.volume_24h == 50052.38095  # somma dei volumi
        assert aggregated.status == "active"  # majority vote
        assert aggregated.id == "BTC-USD_AGG"  # mapping_id con suffisso aggregazione
        
    def test_confidence_calculation(self):
        """Test del calcolo della confidence"""
        
        product1 = ProductInfo(
            id="BTC-USD",
            symbol="BTC-USD",
            price=50000.0,
            volume_24h=1000.0,
            status="active",
            quote_currency="USD"
        )
        
        product2 = ProductInfo(
            id="BTC-USD",
            symbol="BTC-USD",
            price=50100.0,
            volume_24h=1100.0,
            status="active",
            quote_currency="USD"
        )
        
        aggregated = AggregatedProductInfo.from_multiple_sources([product1, product2])
        
        # Verifica che ci siano metadati
        assert aggregated._metadata is not None
        assert len(aggregated._metadata.sources_used) > 0
        assert aggregated._metadata.aggregation_timestamp != ""
        # La confidence può essere 0.0 se ci sono fonti "unknown"


if __name__ == "__main__":
    pytest.main([__file__])