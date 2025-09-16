from dotenv import load_dotenv
from enum import Enum

from agno.agent import Agent
from agno.models.base import BaseModel
from agno.models.google import Gemini
from agno.models.ollama import Ollama
from agno.tools.reasoning import ReasoningTools

class Model(Enum):
    """
    Enum per i modelli supportati.
    Aggiungere nuovi modelli qui se necessario.
    Per quanto riguarda Ollama, i modelli dovrano essere scaricati e installati
    localmente seguendo le istruzioni di https://ollama.com/docs/guide/install-models
    """
    GEMINI = "gemini-2.0-flash" # API online
    OLLAMA = "llama3.1" # little and fast (7b) but not so good
    OLLAMA_GPT = "gpt-oss" # a bit big (13b) but very good (almost like gemini API)
    OLLAMA_GEMMA = "gemma3:4b" # no tool support
    OLLAMA_DEEP = "deepseek-r1:8b" # no tool support
    OLLAMA_QWEN = "qwen3:8b" # good

def get_model(model: Model, instructions:str = None) -> BaseModel:
    """
    Restituisce un'istanza del modello specificato.
    """
    name = model.value

    if model in {Model.GEMINI}:
        return Gemini(name, instructions=instructions)
    elif model in {Model.OLLAMA, Model.OLLAMA_GPT, Model.OLLAMA_GEMMA, Model.OLLAMA_DEEP, Model.OLLAMA_QWEN}:
        return Ollama(name, instructions=instructions)

    raise ValueError(f"Modello non supportato: {model}")

def build_agent(model:Model, instructions: str) -> Agent:
    """
    Costruisce un agente con il modello e le istruzioni specificate.
    """
    return Agent(
        model=get_model(model, instructions=instructions),
        tools=[ReasoningTools()],
        instructions=instructions,
        markdown=True,
    )



if __name__ == "__main__":
    # da fare assolutamente prima di usare tutto perchè carica le variabili d'ambiente
    # come le API key nel nostro caso
    load_dotenv() 

    prompt = "Scrivi una poesia su un gatto."
    instructions = "Rispondi in italiano e molto brevemente. Usa tabelle per visualizzare i dati."

    gemini = build_agent(Model.GEMINI, instructions=instructions).run(prompt)
    print(f"Risposta Gemini:\n{gemini.content}\n==============================")

    ollama = build_agent(Model.OLLAMA_GPT, instructions=instructions).run(prompt)
    print(f"\nRisposta Ollama GPT:\n{ollama.content}\n==============================")

