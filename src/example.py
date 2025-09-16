from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
import ollama
from ollama_demo import generate_text

def run_gemini_poem():
    load_dotenv()
    reasoning_agent = Agent(
        model=Gemini(),
        tools=[ReasoningTools()],
        instructions="Use tables to display data.",
        markdown=True,
    )
    result = reasoning_agent.run("Scrivi una poesia su un gatto. Sii breve.")
    print(result.content)

def run_ollama_codegemma_poem():
    prompt = "Scrivi una poesia su un gatto. Sii breve."
    response = generate_text(model="gpt-oss:latest", prompt=prompt)
    print(response)

if __name__ == "__main__":
    print("Risposta Gemini:")
    run_gemini_poem()
    print("\nRisposta Ollama GPT-OSS:")
    run_ollama_codegemma_poem()
