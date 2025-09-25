#!/usr/bin/env python3
"""
Demo di Ollama (Python) – mostra:
    1. Elenco dei modelli disponibili
    2. Generazione di testo semplice
    3. Chat con streaming
    4. Calcolo di embeddings
    5. Esempio (opzionale) di function calling / tools

Uso:
    python ollama_demo.py

Requisiti:
    pip install ollama
    Avviare il server Ollama (es. 'ollama serve' o l'app desktop) e avere i modelli già pullati.
"""

import ollama

# Configurazione modelli
MODEL = 'gpt-oss:latest'                # modello principale per testo/chat
EMBEDDING_MODEL = 'mxbai-embed-large:latest'  # modello dedicato embeddings (richiede supporto embeddings)

# 1. Elenco dei modelli -------------------------------------------------------

def list_models():
    """Stampa i modelli caricati nel server Ollama."""
    print("\n[1] Modelli disponibili:")
    try:
        response = ollama.list()
        models = getattr(response, 'models', []) or (response.get('models', []) if isinstance(response, dict) else [])
        if not models:
            print("  (Nessun modello trovato)")
            return
        for m in models:
            name = getattr(m, 'model', None) or (m.get('model') if isinstance(m, dict) else 'sconosciuto')
            details = getattr(m, 'details', None)
            fmt = getattr(details, 'format', None) if details else 'unknown'
            print(f"  • {name} – {fmt}")
    except Exception as e:
        print(f"  ❌ Errore durante il listing: {e}")


# 2. Generazione di testo ------------------------------------------------------

def generate_text(model: str, prompt: str, max_tokens: int = 200) -> str:
    """Genera testo dal modello indicato."""
    print(f"\n[2] Generazione testo con '{model}'")
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response['message']['content']
    print("Risposta:\n" + text + "\n")
    return text


# 3. Chat con streaming --------------------------------------------------------

def chat_streaming(model: str, messages: list) -> str:
    """Esegue una chat mostrando progressivamente la risposta."""
    print(f"\n[3] Chat (streaming) con '{model}'")
    stream = ollama.chat(model=model, messages=messages, stream=True)
    full = ""
    for chunk in stream:
        if 'message' in chunk and 'content' in chunk['message']:
            part = chunk['message']['content']
            full += part
            print(part, end="", flush=True)
    print("\n")
    return full


# 4. Embeddings ----------------------------------------------------------------

def get_embedding(model: str, text: str):
    """Calcola embedding del testo col modello specificato (se supportato)."""
    print(f"\n[4] Embedding con '{model}'")
    try:
        r = ollama.embeddings(model=model, prompt=text)
    except ollama.ResponseError as e:
        print(f"  ⚠️ Il modello '{model}' non supporta embeddings o errore API: {e}")
        return None
    emb = r['embedding']
    print(f"Dimensione embedding: {len(emb)} (prime 5: {emb[:5]})")
    return emb


# 5. Function calling / Tools (opzionale) --------------------------------------

def try_tools(model: str):
    """Esempio di function calling; se non supportato mostra messaggio informativo."""
    print(f"\n[5] Function calling / tools con '{model}'")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Ottiene condizioni meteo sintetiche di una località (demo)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "Città"},
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": "Che tempo fa a Milano?"}],
            tools=tools
        )
        msg = response['message']
        if 'tool_calls' in msg and msg['tool_calls']:
            tool_call = msg['tool_calls'][0]
            print("Richiesta funzione:", tool_call['function']['name'])
            print("Argomenti:", tool_call['function']['arguments'])
        else:
            print("Risposta modello senza tool call:", msg.get('content', ''))
    except ollama.ResponseError as e:
        if 'does not support tools' in str(e).lower():
            print("Il modello non supporta i tools.")
        else:
            print("Errore API:", e)


# Main -------------------------------------------------------------------------
if __name__ == '__main__':
    # 1. Elenco modelli
    list_models()

    # 2. Prompt semplice
    generate_text(
        model=MODEL,
        prompt="Scrivi una poesia breve su un tramonto al mare. Usa circa 40 parole."
    )

    # 3. Chat con streaming
    chat_streaming(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Sei un assistente conciso e utile."},
            {"role": "user", "content": "Suggerisci 3 consigli per un cappuccino cremoso a casa."}
        ]
    )

    # 4. Embedding (usa modello dedicato se diverso)
    if EMBEDDING_MODEL:
        get_embedding(
            model=EMBEDDING_MODEL,
            text="L'intelligenza artificiale accelera l'innovazione in molti settori."
        )
    else:
        print("\n[4] Salto embedding: nessun modello embedding configurato.")

    # 5. Function calling (opzionale)
    try_tools(MODEL)