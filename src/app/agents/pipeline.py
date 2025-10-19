import asyncio
from enum import Enum
import logging
import random
from typing import Any, Callable
from agno.agent import RunEvent
from agno.team import Team, TeamRunEvent
from agno.tools.reasoning import ReasoningTools
from agno.run.workflow import WorkflowRunEvent
from agno.workflow.step import Step
from agno.workflow.workflow import Workflow

from app.api.tools import *
from app.agents.prompts import *
from app.agents.core import PipelineInputs

logging = logging.getLogger("pipeline")


class PipelineEvent(str, Enum):
    PLANNER = "Planner"
    INFO_RECOVERY = "Info Recovery"
    REPORT_GENERATION = "Report Generation"
    REPORT_TRANSLATION = "Report Translation"
    TOOL_USED = RunEvent.tool_call_completed

    def check_event(self, event: str, step_name: str) -> bool:
        return event == self.value or (WorkflowRunEvent.step_completed and step_name == self.value)


class Pipeline:
    """
    Coordina gli agenti di servizio (Market, News, Social) e il Predictor finale.
    Il Team è orchestrato da qwen3:latest (Ollama), mentre il Predictor è dinamico
    e scelto dall'utente tramite i dropdown dell'interfaccia grafica.
    """

    def __init__(self, inputs: PipelineInputs):
        self.inputs = inputs

    # ======================
    # Core interaction
    # ======================
    def interact(self, listeners: dict[RunEvent | TeamRunEvent, Callable[[PipelineEvent], None]] = {}) -> str:
        """
        Esegue la pipeline di agenti per rispondere alla query dell'utente.
        Args:
            listeners: dizionario di callback per eventi specifici (opzionale)
        Returns:
            La risposta generata dalla pipeline.
        """
        return asyncio.run(self.interact_async(listeners))

    async def interact_async(self, listeners: dict[RunEvent | TeamRunEvent, Callable[[PipelineEvent], None]] = {}) -> str:
        """
        Versione asincrona che esegue la pipeline di agenti per rispondere alla query dell'utente.
        Args:
            listeners: dizionario di callback per eventi specifici (opzionale)
        Returns:
            La risposta generata dalla pipeline.
        """
        run_id = random.randint(1000, 9999) # Per tracciare i log
        logging.info(f"[{run_id}] Pipeline query: {self.inputs.user_query}")

        # Step 1: Crea gli agenti e il team
        market_tool, news_tool, social_tool = self.get_tools()
        market_agent = self.inputs.team_model.get_agent(instructions=MARKET_INSTRUCTIONS, name="MarketAgent", tools=[market_tool])
        news_agent = self.inputs.team_model.get_agent(instructions=NEWS_INSTRUCTIONS, name="NewsAgent", tools=[news_tool])
        social_agent = self.inputs.team_model.get_agent(instructions=SOCIAL_INSTRUCTIONS, name="SocialAgent", tools=[social_tool])

        team = Team(
            model=self.inputs.team_leader_model.get_model(COORDINATOR_INSTRUCTIONS),
            name="CryptoAnalysisTeam",
            tools=[ReasoningTools()],
            members=[market_agent, news_agent, social_agent],
        )

        # Step 3: Crea il workflow
        #query_planner = Step(name=PipelineEvent.PLANNER, agent=Agent())
        info_recovery = Step(name=PipelineEvent.INFO_RECOVERY, team=team)
        #report_generation = Step(name=PipelineEvent.REPORT_GENERATION, agent=Agent())
        #report_translate = Step(name=AppEvent.REPORT_TRANSLATION, agent=Agent())

        workflow = Workflow(
            name="App Workflow",
            steps=[
                #query_planner,
                info_recovery,
                #report_generation,
                #report_translate
            ]
        )

        # Step 4: Fai partire il workflow e prendi l'output
        query = f"The user query is: {self.inputs.user_query}\n\n They requested a {self.inputs.strategy.label} investment strategy."
        result = await self.run(workflow, query, events={})
        logging.info(f"[{run_id}] Run finished")
        return result

    # ======================
    # Helpers
    # =====================
    def get_tools(self) -> tuple[MarketAPIsTool, NewsAPIsTool, SocialAPIsTool]:
        """
        Restituisce la lista di tools disponibili per gli agenti.
        """
        api = self.inputs.configs.api

        market_tool = MarketAPIsTool(currency=api.currency)
        market_tool.handler.set_retries(api.retry_attempts, api.retry_delay_seconds)
        news_tool = NewsAPIsTool()
        news_tool.handler.set_retries(api.retry_attempts, api.retry_delay_seconds)
        social_tool = SocialAPIsTool()
        social_tool.handler.set_retries(api.retry_attempts, api.retry_delay_seconds)

        return (market_tool, news_tool, social_tool)

    @classmethod
    async def run(cls, workflow: Workflow, query: str, events: dict[PipelineEvent, Callable[[Any], None]]) -> str:
        """
        Esegue il workflow e gestisce gli eventi tramite le callback fornite.
        Args:
            workflow: istanza di Workflow da eseguire
            query: query dell'utente da passare al workflow
            events: dizionario di callback per eventi specifici (opzionale)
        Returns:
            La risposta generata dal workflow.
        """
        iterator = await workflow.arun(query, stream=True, stream_intermediate_steps=True)

        content = None
        async for event in iterator:
            step_name = getattr(event, 'step_name', '')

            for app_event, listener in events.items():
                if app_event.check_event(event.event, step_name):
                    listener(event)

            if event.event == WorkflowRunEvent.workflow_completed:
                content = getattr(event, 'content', '')
                if isinstance(content, str):
                    think_str = "</think>"
                    think = content.rfind(think_str)
                    content = content[(think + len(think_str)):] if think != -1 else content

        return content if content else "No output from workflow, something went wrong."
