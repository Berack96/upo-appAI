import os
import json
from typing import List, Dict
from pipeline import Pipeline

SAVE_DIR = os.path.join(os.path.dirname(__file__), "..", "saves")
os.makedirs(SAVE_DIR, exist_ok=True)

class ChatManager:
    """
    Gestisce la conversazione con la Pipeline:
    - mantiene lo storico dei messaggi
    - invoca la Pipeline per generare risposte
    - salva e ricarica le chat
    """

    def __init__(self):
        self.pipeline = Pipeline()
        self.history: List[Dict[str, str]] = []  # [{"role": "user"/"assistant", "content": "..."}]

    def send_message(self, message: str) -> str:
        """
        Aggiunge un messaggio utente, chiama la Pipeline e salva la risposta nello storico.
        """
        # Aggiungi messaggio utente allo storico
        self.history.append({"role": "user", "content": message})

        # Pipeline elabora la query
        response = self.pipeline.interact(message)

        # Aggiungi risposta assistente allo storico
        self.history.append({"role": "assistant", "content": response})

        return response

    def save_chat(self, filename: str = "chat.json") -> None:
        """
        Salva la chat corrente in src/saves/<filename>.
        """
        path = os.path.join(SAVE_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def load_chat(self, filename: str = "chat.json") -> None:
        """
        Carica una chat salvata da src/saves/<filename>.
        """
        path = os.path.join(SAVE_DIR, filename)
        if not os.path.exists(path):
            self.history = []
            return
        with open(path, "r", encoding="utf-8") as f:
            self.history = json.load(f)

    def reset_chat(self) -> None:
        """
        Resetta lo storico della chat.
        """
        self.history = []

    def get_history(self) -> List[Dict[str, str]]:
        """
        Restituisce lo storico completo della chat.
        """
        return self.history

    # Facciamo pass-through di provider e style, così Gradio può usarli
    def choose_provider(self, index: int):
        self.pipeline.choose_provider(index)

    def choose_style(self, index: int):
        self.pipeline.choose_style(index)

    def list_providers(self) -> List[str]:
        return self.pipeline.list_providers()

    def list_styles(self) -> List[str]:
        return self.pipeline.list_styles()
