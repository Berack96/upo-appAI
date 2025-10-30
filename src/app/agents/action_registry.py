# Registro popolato da tutti i file Toolkit presenti all'avvio.
ACTION_DESCRIPTIONS: dict[str, str] = {}

def register_friendly_actions(actions: dict[str, str]):
    """
    Aggiunge le descrizioni di un Toolkit al registro globale.
    """
    global ACTION_DESCRIPTIONS
    ACTION_DESCRIPTIONS.update(actions)