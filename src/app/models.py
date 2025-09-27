import os
import requests
from enum import Enum
from agno.agent import Agent
from agno.models.base import BaseModel
from agno.models.google import Gemini
from agno.models.ollama import Ollama

from agno.utils.log import log_warning

class Models(Enum):
    """
    Enum per i modelli supportati.
    Aggiungere nuovi modelli qui se necessario.
    Per quanto riguarda Ollama, i modelli dovranno essere scaricati e installati
    localmente seguendo le istruzioni di https://ollama.com/docs/guide/install-models
    """
    GEMINI = "gemini-2.0-flash" # API online
    GEMINI_PRO = "gemini-2.0-pro" # API online, più costoso ma migliore
    OLLAMA_GPT = "gpt-oss:latest" # + good - slow (13b)
    OLLAMA_QWEN = "qwen3:latest" # + good + fast (8b)

    @staticmethod
    def availables_local() -> list['Models']:
        """
        Controlla quali provider di modelli LLM locali sono disponibili.
        Ritorna una lista di provider disponibili.
        """
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        result = requests.get(f"{ollama_host}/api/tags")
        if result.status_code != 200:
            log_warning(f"Ollama is not running or not reachable {result}")
            return []

        availables = []
        result = result.text
        if Models.OLLAMA_GPT.value in result:
            availables.append(Models.OLLAMA_GPT)
        if Models.OLLAMA_QWEN.value in result:
            availables.append(Models.OLLAMA_QWEN)
        return availables

    def availables_online() -> list['Models']:
        """
        Controlla quali provider di modelli LLM online hanno le loro API keys disponibili
        come variabili d'ambiente e ritorna una lista di provider disponibili.
        """
        if not os.getenv("GOOGLE_API_KEY"):
            log_warning("No GOOGLE_API_KEY set in environment variables.")
            return []
        availables = []
        availables.append(Models.GEMINI)
        availables.append(Models.GEMINI_PRO)
        return availables

    @staticmethod
    def availables() -> list['Models']:
        """
        Controlla quali provider di modelli LLM locali sono disponibili e quali
        provider di modelli LLM online hanno le loro API keys disponibili come variabili
        d'ambiente e ritorna una lista di provider disponibili.
        L'ordine di preferenza è:
        1. Gemini (Google)
        2. Ollama (locale)
        """
        availables = [
            *Models.availables_online(),
            *Models.availables_local()
        ]
        assert availables, "No valid model API keys set in environment variables."
        return availables

    @staticmethod
    def extract_json_str_from_response(response: str) -> str:
        """
        Estrae il JSON dalla risposta del modello.
        response: risposta del modello (stringa).
        Ritorna la parte JSON della risposta come stringa.
        Se non viene trovato nessun JSON, ritorna una stringa vuota.
        ATTENZIONE: questa funzione è molto semplice e potrebbe non funzionare
        in tutti i casi. Si assume che il JSON sia ben formato e che inizi con
        '{' e finisca con '}'. Quindi anche solo un json array farà fallire questa funzione.
        """
        think = response.rfind("</think>")
        if think != -1:
            response = response[think:]

        start = response.find("{")
        assert start != -1, "No JSON found in the response."

        end = response.rfind("}")
        assert end != -1, "No JSON found in the response."

        return response[start:end + 1].strip()


    def get_model(self, instructions:str) -> BaseModel:
        """
        Restituisce un'istanza del modello specificato.
        instructions: istruzioni da passare al modello (system prompt).
        Ritorna un'istanza di BaseModel o una sua sottoclasse.
        Raise ValueError se il modello non è supportato.
        """
        name = self.value
        if self in {Models.GEMINI, Models.GEMINI_PRO}:
            return Gemini(name, instructions=[instructions])
        elif self in {Models.OLLAMA_GPT, Models.OLLAMA_QWEN}:
            return Ollama(name, instructions=[instructions])

        raise ValueError(f"Modello non supportato: {self}")

    def get_agent(self, instructions: str, name: str = "") -> Agent:
        """
        Costruisce un agente con il modello e le istruzioni specificate.
        instructions: istruzioni da passare al modello (system prompt).
        Ritorna un'istanza di Agent.
        """
        return Agent(
            model=self.get_model(instructions),
            name=name,
            retries=2,
            delay_between_retries=5, # seconds
            use_json_mode=True, # utile per fare in modo che l'agente risponda in JSON (anche se sembra essere solo placebo)
            # TODO Eventuali altri parametri da mettere all'agente anche se si possono comunque assegnare dopo la creazione
        )
