# Registro popolato da tutti i file Toolkit presenti all'avvio.
ACTION_DESCRIPTIONS: dict[str, str] = {}

def register_friendly_actions(actions: dict[str, str]):
    """
    Aggiunge le descrizioni di un Toolkit al registro globale.
    """
    global ACTION_DESCRIPTIONS
    ACTION_DESCRIPTIONS.update(actions)

def get_user_friendly_action(tool_name: str) -> str:
    """
    Restituisce un messaggio leggibile e descrittivo per l'utente
    leggendo dal registro globale.
    """
    # Usa il dizionario ACTION_DESCRIPTIONS importato
    return ACTION_DESCRIPTIONS.get(tool_name, f"⚙️ Eseguo l'operazione: {tool_name}...")
