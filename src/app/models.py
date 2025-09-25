import os
from enum import Enum
from agno.agent import Agent
from agno.models.base import BaseModel
from agno.models.google import Gemini
from agno.models.ollama import Ollama

class Models(Enum):
    """
    Enum per i modelli supportati.
    Aggiungere nuovi modelli qui se necessario.
    Per quanto riguarda Ollama, i modelli dovranno essere scaricati e installati
    localmente seguendo le istruzioni di https://ollama.com/docs/guide/install-models
    """
    GEMINI = "gemini-2.0-flash" # API online
    GEMINI_PRO = "gemini-2.0-pro" # API online, più costoso ma migliore
    OLLAMA = "llama3.1" # little and fast (7b) but not so good
    OLLAMA_GPT = "gpt-oss" # a bit big (13b) but very good (almost like gemini API)
    OLLAMA_QWEN = "qwen3:8b" # good
    MOCK = "mock"

    def available() -> list[str]:
        """
        Controlla quali provider di modelli LLM hanno le loro API keys disponibili
        come variabili d'ambiente e ritorna una lista di provider disponibili.
        Se nessuna API key è disponibile, ritorna solo 'mock' come opzione.
        L'ordine di preferenza è:
        1. Gemini (Google)
        2. Ollama (locale)
        """
        availables = []
        if os.getenv("GOOGLE_API_KEY"):
            availables.append(Models.GEMINI)
            availables.append(Models.GEMINI_PRO)
        if os.getenv("OLLAMA_MODELS_PATH"):
            availables.append(Models.OLLAMA)
            availables.append(Models.OLLAMA_GPT)
            availables.append(Models.OLLAMA_QWEN)

        return [Models.MOCK, *availables]

    def __str__(self) -> str:
        # Per semplificare la visualizzazione del modello come stringa.
        return self.name

    def get_model(self, instructions:str) -> BaseModel:
        """
        Restituisce un'istanza del modello specificato.
        instructions: istruzioni da passare al modello (system prompt).
        Ritorna un'istanza di BaseModel o una sua sottoclasse.
        Raise ValueError se il modello non è supportato.
        """
        name = self.value
        if self in {Models.GEMINI}:
            return Gemini(name, instructions=instructions)
        elif self in {Models.OLLAMA, Models.OLLAMA_GPT, Models.OLLAMA_QWEN}:
            return Ollama(name, instructions=instructions)
        elif self in {Models.MOCK}:
            from agno.models.base import Model
            return Model(name, instructions=instructions)

        raise ValueError(f"Modello non supportato: {self}")

    def get_agent(self, instructions: str) -> Agent:
        """
        Costruisce un agente con il modello e le istruzioni specificate.
        instructions: istruzioni da passare al modello (system prompt).
        Ritorna un'istanza di Agent.
        """
        return Agent(
            model=self.get_model(instructions=instructions),
            instructions=instructions,
            # TODO Eventuali altri parametri da mettere all'agente
            # anche se si possono comunque assegnare dopo la creazione
            # Esempio:
            # retries=2,
            # retry_delay=1,
        )
