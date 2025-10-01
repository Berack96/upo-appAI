"""
Configurazione pytest per i test del progetto upo-appAI.
"""

import pytest
from dotenv import load_dotenv

# Carica le variabili d'ambiente per tutti i test
load_dotenv()


def pytest_configure(config:pytest.Config):
    """Configurazione pytest con marker personalizzati"""

    markers = [
        ("slow", "marks tests as slow (deselect with '-m \"not slow\"')"),
        ("api", "marks tests that require API access"),
        ("market", "marks tests that use market data"),
        ("gemini", "marks tests that use Gemini model"),
        ("ollama_gpt", "marks tests that use Ollama GPT model"),
        ("ollama_qwen", "marks tests that use Ollama Qwen model"),
        ("news", "marks tests that use news"),
        ("social", "marks tests that use social media"),
        ("limited", "marks tests that have limited execution due to API constraints"),
        ("wrapper", "marks tests for wrapper handler"),
        ("tools", "marks tests for tools"),
        ("aggregator", "marks tests for market data aggregator"),
    ]
    for marker in markers:
        line = f"{marker[0]}: {marker[1]}"
        config.addinivalue_line("markers", line)

def pytest_collection_modifyitems(config, items):
    """Modifica automaticamente degli item di test rimovendoli"""
    # Rimuovo i test "limited" e "slow" se non richiesti esplicitamente
    mark_to_remove = ['limited', 'slow']
    for mark in mark_to_remove:
        markexpr = getattr(config.option, "markexpr", None)
        if markexpr and mark in markexpr.lower():
            continue

        new_mark = (f"({markexpr}) and " if markexpr else "") + f"not {mark}"
        setattr(config.option, "markexpr", new_mark)
