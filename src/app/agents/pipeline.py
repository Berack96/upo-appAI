import asyncio
from enum import Enum
import logging
import random
from typing import Any, Callable
from agno.agent import RunEvent
from agno.team import Team
from agno.tools.reasoning import ReasoningTools
from agno.run.workflow import WorkflowRunEvent
from agno.workflow.types import StepInput, StepOutput
from agno.workflow.step import Step
from agno.workflow.workflow import Workflow
from app.api.tools import *
from app.agents.prompts import *
from app.agents.core import *

logging = logging.getLogger("pipeline")



class PipelineEvent(str, Enum):
    QUERY_CHECK = "Query Check"
    QUERY_ANALYZER = "Query Analyzer"
    INFO_RECOVERY = "Info Recovery"
    REPORT_GENERATION = "Report Generation"
    REPORT_TRANSLATION = "Report Translation"
    RUN_FINISHED = WorkflowRunEvent.workflow_completed
    TOOL_USED = RunEvent.tool_call_completed

    def check_event(self, event: str, step_name: str) -> bool:
        return event == self.value or (WorkflowRunEvent.step_completed == event and step_name == self.value)

    @classmethod
    def get_log_events(cls, run_id: int) -> list[tuple['PipelineEvent', Callable[[Any], None]]]:
        return [
            (PipelineEvent.QUERY_CHECK, lambda _: logging.info(f"[{run_id}] Query Check completed.")),
            (PipelineEvent.QUERY_ANALYZER, lambda _: logging.info(f"[{run_id}] Query Analyzer completed.")),
            (PipelineEvent.INFO_RECOVERY, lambda _: logging.info(f"[{run_id}] Info Recovery completed.")),
            (PipelineEvent.REPORT_GENERATION, lambda _: logging.info(f"[{run_id}] Report Generation completed.")),
            (PipelineEvent.TOOL_USED, lambda e: logging.info(f"[{run_id}] Tool used: {getattr(e, 'tool_name', 'unknown')}")),
            (PipelineEvent.RUN_FINISHED, lambda _: logging.info(f"[{run_id}] Run completed.")),
        ]


class Pipeline:
    """
    Coordina gli agenti di servizio (Market, News, Social) e il Predictor finale.
    Il Team è orchestrato da qwen3:latest (Ollama), mentre il Predictor è dinamico
    e scelto dall'utente tramite i dropdown dell'interfaccia grafica.
    """

    def __init__(self, inputs: PipelineInputs):
        self.inputs = inputs

    def interact(self, listeners: list[tuple[PipelineEvent, Callable[[Any], None]]] = []) -> str:
        """
        Esegue la pipeline di agenti per rispondere alla query dell'utente.
        Args:
            listeners: dizionario di callback per eventi specifici (opzionale)
        Returns:
            La risposta generata dalla pipeline.
        """
        return asyncio.run(self.interact_async(listeners))

    async def interact_async(self, listeners: list[tuple[PipelineEvent, Callable[[Any], None]]] = []) -> str:
        """
        Versione asincrona che esegue la pipeline di agenti per rispondere alla query dell'utente.
        Args:
            listeners: dizionario di callback per eventi specifici (opzionale)
        Returns:
            La risposta generata dalla pipeline.
        """
        run_id = random.randint(1000, 9999) # Per tracciare i log
        logging.info(f"[{run_id}] Pipeline query: {self.inputs.user_query}")

        events = [*PipelineEvent.get_log_events(run_id), *listeners]
        query = QueryInputs(
            user_query=self.inputs.user_query,
            strategy=self.inputs.strategy.description
        )

        workflow = self.build_workflow()
        result = await self.run(workflow, query, events=events)
        return result


    def build_workflow(self) -> Workflow:
        """
        Costruisce il workflow della pipeline di agenti.
        Returns:
            L'istanza di Workflow costruita.
        """
        # Step 1: Crea gli agenti e il team
        q_check_agent = self.inputs.query_analyzer_model.get_agent(instructions=QUERY_CHECK_INSTRUCTIONS, name="QueryCheckAgent", output_schema=QueryOutputs)
        report_agent = self.inputs.report_generation_model.get_agent(instructions=REPORT_GENERATION_INSTRUCTIONS, name="ReportGeneratorAgent")

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

        # Step 2: Crea gli steps
        def condition_query_ok(step_input: StepInput) -> StepOutput:
            val = step_input.previous_step_content
            return StepOutput(stop=not val.is_ok) if isinstance(val, QueryOutputs) else StepOutput(stop=True)

        query_check = Step(name=PipelineEvent.QUERY_CHECK, agent=q_check_agent)
        info_recovery = Step(name=PipelineEvent.INFO_RECOVERY, team=team)
        report_generation = Step(name=PipelineEvent.REPORT_GENERATION, agent=report_agent)

        # Step 3: Ritorna il workflow completo
        return Workflow(name="App Workflow", steps=[
            query_check,
            condition_query_ok,
            info_recovery,
            report_generation
        ])


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
    async def run(cls, workflow: Workflow, query: QueryInputs, events: list[tuple[PipelineEvent, Callable[[Any], None]]]) -> str:
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
            for app_event, listener in events:
                if app_event.check_event(event.event, step_name):
                    listener(event)
            if event.event == WorkflowRunEvent.step_completed:
                content = getattr(event, 'content', '')

        if content and isinstance(content, str):
            think_str = "</think>"
            think = content.rfind(think_str)
            return content[(think + len(think_str)):] if think != -1 else content
        if content and isinstance(content, QueryOutputs):
            return content.response

        logging.error(f"No output from workflow: {content}")
        return "No output from workflow, something went wrong."
