import os
import requests
from enum import Enum
from agno.agent import Agent
from agno.models.base import Model
from agno.models.google import Gemini
from agno.models.ollama import Ollama
from agno.tools import Toolkit
from agno.utils.log import log_warning #type: ignore
from pydantic import BaseModel


class AppModels(Enum):
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
    OLLAMA_QWEN_4B = "qwen3:4b" # + fast + decent (4b)
    OLLAMA_QWEN_1B = "qwen3:1.7b" # + very fast + decent (1.7b)

    @staticmethod
    def availables_local() -> list['AppModels']:
        """
        Controlla quali provider di modelli LLM locali sono disponibili.
        Ritorna una lista di provider disponibili.
        """
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        result = requests.get(f"{ollama_host}/api/tags")
        if result.status_code != 200:
            log_warning(f"Ollama is not running or not reachable {result}")
            return []

        availables: list[AppModels] = []
        result = result.text
        for model in [model for model in AppModels if model.name.startswith("OLLAMA")]:
            if model.value in result:
                availables.append(model)
        return availables

    @staticmethod
    def availables_online() -> list['AppModels']:
        """
        Controlla quali provider di modelli LLM online hanno le loro API keys disponibili
        come variabili d'ambiente e ritorna una lista di provider disponibili.
        """
        if not os.getenv("GOOGLE_API_KEY"):
            log_warning("No GOOGLE_API_KEY set in environment variables.")
            return []
        availables = [AppModels.GEMINI, AppModels.GEMINI_PRO]
        return availables

    @staticmethod
    def availables() -> list['AppModels']:
        """
        Controlla quali provider di modelli LLM locali sono disponibili e quali
        provider di modelli LLM online hanno le loro API keys disponibili come variabili
        d'ambiente e ritorna una lista di provider disponibili.
        L'ordine di preferenza è:
        1. Gemini (Google)
        2. Ollama (locale)
        """
        availables = [
            *AppModels.availables_online(),
            *AppModels.availables_local()
        ]
        assert availables, "No valid model API keys set in environment variables."
        return availables

    def get_model(self, instructions:str) -> Model:
        """
        Restituisce un'istanza del modello specificato.
        Args:
            instructions: istruzioni da passare al modello (system prompt).
        Returns:
             Un'istanza di BaseModel o una sua sottoclasse.
        Raise:
            ValueError se il modello non è supportato.
        """
        name = self.value
        if self in {model for model in AppModels if model.name.startswith("GEMINI")}:
            return Gemini(name, instructions=[instructions])
        elif self in {model for model in AppModels if model.name.startswith("OLLAMA")}:
            return Ollama(name, instructions=[instructions])

        raise ValueError(f"Modello non supportato: {self}")

    def get_agent(self, instructions: str, name: str = "", output: BaseModel | None = None, tools: list[Toolkit] = []) -> Agent:
        """
        Costruisce un agente con il modello e le istruzioni specificate.
        Args:
            instructions: istruzioni da passare al modello (system prompt)
            name: nome dell'agente (opzionale)
            output: schema di output opzionale (Pydantic BaseModel)
        Returns:
             Un'istanza di Agent.
        """
        return Agent(
            model=self.get_model(instructions),
            name=name,
            retries=2,
            tools=tools,
            delay_between_retries=5, # seconds
            output_schema=output.__class__ if output else None # se si usa uno schema di output, lo si passa qui
        )
