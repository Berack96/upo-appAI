from enum import Enum
import logging
import random
from typing import Any, AsyncGenerator, Callable
from agno.agent import RunEvent
from agno.run.workflow import WorkflowRunEvent
from agno.workflow.types import StepInput, StepOutput
from agno.workflow.step import Step
from agno.workflow.workflow import Workflow
from app.agents.core import *

logging = logging.getLogger("pipeline")


class PipelineEvent(str, Enum):
    QUERY_CHECK = "Query Check"
    QUERY_CHECK_END = "Query Check End"
    INFO_RECOVERY = "Info Recovery"
    INFO_RECOVERY_END = "Info Recovery End"
    REPORT_GENERATION = "Report Generation"
    REPORT_GENERATION_END = "Report Generation End"
    TOOL_USED = RunEvent.tool_call_started.value
    TOOL_USED_END = RunEvent.tool_call_completed.value
    RUN_END = WorkflowRunEvent.workflow_completed.value

    def check_event(self, event: str, step_name: str) -> bool:
        if event == self.value:
            return True

        index = self.value.rfind(" End")
        value = self.value[:index] if index > -1 else self.value
        step_state = WorkflowRunEvent.step_completed if index > -1 else WorkflowRunEvent.step_started
        return step_name == value and step_state == event

    @classmethod
    def get_log_events(cls, run_id: int) -> list[tuple['PipelineEvent', Callable[[Any], str | None]]]:
        return [
            (PipelineEvent.QUERY_CHECK_END, lambda _: logging.info(f"[{run_id}] Query Check completed.")),
            (PipelineEvent.INFO_RECOVERY_END, lambda _: logging.info(f"[{run_id}] Info Recovery completed.")),
            (PipelineEvent.REPORT_GENERATION_END, lambda _: logging.info(f"[{run_id}] Report Generation completed.")),
            (PipelineEvent.TOOL_USED_END, lambda e: logging.info(f"[{run_id}] Tool used [{e.tool.tool_name} {e.tool.tool_args}] by {e.agent_name}.")),
            (PipelineEvent.RUN_END, lambda _: logging.info(f"[{run_id}] Run completed.")),
        ]


class Pipeline:
    """
    Coordina gli agenti di servizio (Market, News, Social) e il Predictor finale.
    Il Team è orchestrato da qwen3:latest (Ollama), mentre il Predictor è dinamico
    e scelto dall'utente tramite i dropdown dell'interfaccia grafica.
    """

    def __init__(self, inputs: PipelineInputs):
        """
        Inizializza la pipeline con gli input forniti.
        Args:
            inputs: istanza di PipelineInputs contenente le configurazioni e i parametri della pipeline.
        """
        self.inputs = inputs

    async def interact(self, listeners: list[tuple[PipelineEvent, Callable[[Any], str | None]]] = []) -> str:
        """
        Esegue la pipeline di agenti per rispondere alla query dell'utente.
        Args:
            listeners: dizionario di callback per eventi specifici (opzionale)
        Returns:
            La risposta generata dalla pipeline.
        """
        response = ""
        async for chunk in self.interact_stream(listeners):
            response = chunk
        return response

    async def interact_stream(self, listeners: list[tuple[PipelineEvent, Callable[[Any], str | None]]] = []) -> AsyncGenerator[str, None]:
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
        async for item in self.run_stream(workflow, query, events=events):
            yield item

    def build_workflow(self) -> Workflow:
        """
        Costruisce il workflow della pipeline di agenti.
        Returns:
            L'istanza di Workflow costruita.
        """
        # Step 1: Crea gli agenti e il team
        team = self.inputs.get_agent_team()
        query_check = self.inputs.get_agent_query_checker()
        report = self.inputs.get_agent_report_generator()

        # Step 2: Crea gli steps
        def condition_query_ok(step_input: StepInput) -> StepOutput:
            val = step_input.previous_step_content
            stop = (not val.is_crypto) if isinstance(val, QueryOutputs) else True
            return StepOutput(stop=stop, content=step_input.input)

        def sanitization_output(step_input: StepInput) -> StepOutput:
            val = step_input.previous_step_content
            content = f"Query: {step_input.input}\n\nRetrieved data: {self.remove_think(str(val))}"
            return StepOutput(content=content)

        query_check = Step(name=PipelineEvent.QUERY_CHECK, agent=query_check)
        info_recovery = Step(name=PipelineEvent.INFO_RECOVERY, team=team)
        report_generation = Step(name=PipelineEvent.REPORT_GENERATION, agent=report)

        # Step 3: Ritorna il workflow completo
        return Workflow(name="App Workflow", steps=[
            query_check,
            condition_query_ok,
            info_recovery,
            sanitization_output,
            report_generation
        ])

    @classmethod
    async def run_stream(cls, workflow: Workflow, query: QueryInputs, events: list[tuple[PipelineEvent, Callable[[Any], str | None]]]) -> AsyncGenerator[str, None]:
        """
        Esegue il workflow e restituisce gli eventi di stato e il risultato finale.
        Args:
            workflow: L'istanza di Workflow da eseguire
            query: Gli input della query
            events: La lista di eventi e callback da gestire durante l'esecuzione.
        Yields:
            Aggiornamenti di stato e la risposta finale generata dal workflow.
        """
        iterator = await workflow.arun(query, stream=True, stream_intermediate_steps=True)
        content = None

        async for event in iterator:
            step_name = getattr(event, 'step_name', '')

            # Chiama i listeners (se presenti) per ogni evento
            for app_event, listener in events:
                if app_event.check_event(event.event, step_name):
                    update = listener(event)
                    if update: yield update

            # Salva il contenuto finale quando uno step è completato
            if event.event == WorkflowRunEvent.step_completed.value:
                content = getattr(event, 'content', '')

        # Restituisce la risposta finale
        if content and isinstance(content, str):
            yield cls.remove_think(content)
        elif content and isinstance(content, QueryOutputs):
            yield content.response
        else:
            logging.error(f"No output from workflow: {content}")
            yield "Nessun output dal workflow, qualcosa è andato storto."

    @classmethod
    def remove_think(cls, text: str) -> str:
        """
        Rimuove la sezione di pensiero dal testo.
        Args:
            text: Il testo da pulire.
        Returns:
            Il testo senza la sezione di pensiero.
        """
        think_str = "</think>"
        think = text.rfind(think_str)
        return text[(think + len(think_str)):] if think != -1 else text
