from typing import Any, Callable


# Registro centrale popolato da tutti i file Toolkit all'avvio.
ACTION_DESCRIPTIONS: dict[str, str] = {}

def get_user_friendly_action(tool_name: str) -> str:
    """
    Restituisce un messaggio leggibile e descrittivo per l'utente
    leggendo dal registro globale.
    """
    # Usa il dizionario ACTION_DESCRIPTIONS importato
    return ACTION_DESCRIPTIONS.get(tool_name, f"⚙️ Eseguo l'operazione: {tool_name}...")

def friendly_action(description: str) -> Callable[..., Any]:
    """
    Decoratore che registra automaticamente la descrizione "user-friendly"
    di un metodo nel registro globale.

    Questo decoratore viene eseguito all'avvio dell'app (quando i file
    vengono importati) e popola il dizionario ACTION_DESCRIPTIONS.

    Restituisce la funzione originale non modificata.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Registra l'azione
        tool_name = func.__name__
        if tool_name in ACTION_DESCRIPTIONS:
            print(f"Attenzione: Azione '{tool_name}' registrata più volte.")

        ACTION_DESCRIPTIONS[tool_name] = description

        # Restituisce la funzione originale
        return func

    return decorator
