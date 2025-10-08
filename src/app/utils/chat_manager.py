import json
import os

class ChatManager:
    """
    Gestisce la conversazione con la Pipeline:
    - mantiene lo storico dei messaggi
    - invoca la Pipeline per generare risposte
    - salva e ricarica le chat
    """

    def __init__(self):
        self.history: list[dict[str, str]] = []  # [{"role": "user"/"assistant", "content": "..."}]

    def send_message(self, message: str) -> None:
        """
        Aggiunge un messaggio utente, chiama la Pipeline e salva la risposta nello storico.
        """
        # Aggiungi messaggio utente allo storico
        self.history.append({"role": "user", "content": message})

    def receive_message(self, response: str) -> str:
        """
        Riceve un messaggio dalla pipeline e lo aggiunge allo storico.
        """
        # Aggiungi risposta assistente allo storico
        self.history.append({"role": "assistant", "content": response})

        return response

    def save_chat(self, filename: str = "chat.json") -> None:
        """
        Salva la chat corrente in src/saves/<filename>.
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def load_chat(self, filename: str = "chat.json") -> None:
        """
        Carica una chat salvata da src/saves/<filename>.
        """
        if not os.path.exists(filename):
            self.history = []
            return
        with open(filename, "r", encoding="utf-8") as f:
            self.history = json.load(f)

    def reset_chat(self) -> None:
        """
        Resetta lo storico della chat.
        """
        self.history = []

    def get_history(self) -> list[dict[str, str]]:
        """
        Restituisce lo storico completo della chat.
        """
        return self.history
