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


def pytest_configure(config:pytest.Config):
    """Configurazione pytest con marker personalizzati"""

    markers = [
        ("slow", "marks tests as slow (deselect with '-m \"not slow\"')"),
        ("api", "marks tests that require API access"),
        ("coinbase", "marks tests that require Coinbase credentials"),
        ("cryptocompare", "marks tests that require CryptoCompare credentials"),
        ("gemini", "marks tests that use Gemini model"),
        ("ollama_gpt", "marks tests that use Ollama GPT model"),
        ("ollama_qwen", "marks tests that use Ollama Qwen model"),
    ]
    for marker in markers:
        line = f"{marker[0]}: {marker[1]}"
        config.addinivalue_line("markers", line)

def pytest_collection_modifyitems(config, items):
    """Modifica automaticamente gli item di test aggiungendogli marker basati sul nome"""

    markers_to_add = {
        "api": pytest.mark.api,
        "coinbase": pytest.mark.api,
        "cryptocompare": pytest.mark.api,
        "overview": pytest.mark.slow,
        "analysis": pytest.mark.slow,
        "gemini": pytest.mark.gemini,
        "ollama_gpt": pytest.mark.ollama_gpt,
        "ollama_qwen": pytest.mark.ollama_qwen,
    }

    for item in items:
        name = item.name.lower()
        for key, marker in markers_to_add.items():
            if key in name:
                item.add_marker(marker)
