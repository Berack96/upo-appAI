#### FOR ALL FILES OUTSIDE src/ FOLDER ####
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
###########################################

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv

try:
    load_dotenv()

    reasoning_agent = Agent(
        model=Gemini(),
        tools=[ReasoningTools()],
        instructions="Use tables to display data.",
        markdown=True,
    )
    result = reasoning_agent.run("Scrivi una poesia su un gatto. Sii breve.")
    print(result.content)
except Exception as e:
    print(f"Si è verificato un errore: {e}")
