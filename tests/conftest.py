"""
Configurazione pytest per i test del progetto upo-appAI.
"""

import sys
import pytest
from pathlib import Path

# Aggiungi il path src al PYTHONPATH per tutti i test
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Carica le variabili d'ambiente per tutti i test
from dotenv import load_dotenv
load_dotenv()


def pytest_configure(config):
    """Configurazione pytest"""
    # Aggiungi marker personalizzati
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API access"
    )
    config.addinivalue_line(
        "markers", "coinbase: marks tests that require Coinbase credentials"
    )
    config.addinivalue_line(
        "markers", "cryptocompare: marks tests that require CryptoCompare credentials"
    )


def pytest_collection_modifyitems(config, items):
    """Modifica automaticamente gli item di test"""
    # Aggiungi marker 'api' a tutti i test che richiedono API
    for item in items:
        if "api" in item.name.lower() or "coinbase" in item.name.lower() or "cryptocompare" in item.name.lower():
            item.add_marker(pytest.mark.api)

        # Aggiungi marker 'slow' ai test che potrebbero essere lenti
        if "overview" in item.name.lower() or "analysis" in item.name.lower():
            item.add_marker(pytest.mark.slow)
