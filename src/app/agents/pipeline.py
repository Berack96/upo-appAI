import asyncio
from enum import Enum
import logging
import random
from typing import Any, Callable
from agno.agent import RunEvent
from agno.run.workflow import WorkflowRunEvent
from agno.workflow.types import StepInput, StepOutput
from agno.workflow.step import Step
from agno.workflow.workflow import Workflow
from app.agents.core import *

logging = logging.getLogger("pipeline")



class PipelineEvent(str, Enum):
    QUERY_CHECK = "Query Check"
    QUERY_ANALYZER = "Query Analyzer"
    INFO_RECOVERY = "Info Recovery"
    REPORT_GENERATION = "Report Generation"
    REPORT_TRANSLATION = "Report Translation"
    RUN_FINISHED = WorkflowRunEvent.workflow_completed.value
    TOOL_USED = RunEvent.tool_call_completed.value

    def check_event(self, event: str, step_name: str) -> bool:
        return event == self.value or (WorkflowRunEvent.step_completed == event and step_name == self.value)

    @classmethod
    def get_log_events(cls, run_id: int) -> list[tuple['PipelineEvent', Callable[[Any], None]]]:
        return [
            (PipelineEvent.QUERY_CHECK, lambda _: logging.info(f"[{run_id}] Query Check completed.")),
            (PipelineEvent.QUERY_ANALYZER, lambda _: logging.info(f"[{run_id}] Query Analyzer completed.")),
            (PipelineEvent.INFO_RECOVERY, lambda _: logging.info(f"[{run_id}] Info Recovery completed.")),
            (PipelineEvent.REPORT_GENERATION, lambda _: logging.info(f"[{run_id}] Report Generation completed.")),
            (PipelineEvent.TOOL_USED, lambda e: logging.info(f"[{run_id}] Tool used [{e.tool.tool_name} {e.tool.tool_args}] by {e.agent_name}.")),
            (PipelineEvent.RUN_FINISHED, lambda _: logging.info(f"[{run_id}] Run completed.")),
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

    async def interact_stream(self, listeners: list[tuple[PipelineEvent, Callable[[Any], None]]] = []):
        """
        Versione asincrona in streaming che ESEGUE (yield) la pipeline,
        restituendo gli aggiornamenti di stato e il risultato finale.
        """
        run_id = random.randint(1000, 9999)  # Per tracciare i log
        logging.info(f"[{run_id}] Pipeline query: {self.inputs.user_query}")

        events = [*PipelineEvent.get_log_events(run_id), *listeners]
        query = QueryInputs(
            user_query=self.inputs.user_query,
            strategy=self.inputs.strategy.description
        )

        workflow = self.build_workflow()

        # Delega al classmethod 'run_stream' per lo streaming
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
            return StepOutput(stop=not val.is_crypto) if isinstance(val, QueryOutputs) else StepOutput(stop=True)

        query_check = Step(name=PipelineEvent.QUERY_CHECK, agent=query_check)
        info_recovery = Step(name=PipelineEvent.INFO_RECOVERY, team=team)
        report_generation = Step(name=PipelineEvent.REPORT_GENERATION, agent=report)

        # Step 3: Ritorna il workflow completo
        return Workflow(name="App Workflow", steps=[
            query_check,
            condition_query_ok,
            info_recovery,
            report_generation
        ])

    @classmethod
    async def run(cls, workflow: Workflow, query: QueryInputs,
                  events: list[tuple[PipelineEvent, Callable[[Any], None]]]) -> str:
        """
        Esegue il workflow e gestisce gli eventi, restituendo solo il risultato finale.
        Consuma il generatore 'run_stream'.
        """
        final_result = "Errore durante l'esecuzione del workflow."
        # Consuma il generatore e salva solo l'ultimo item
        async for item in cls.run_stream(workflow, query, events):
            final_result = item

        return final_result

    @classmethod
    async def run_stream(cls, workflow: Workflow, query: QueryInputs,
                         events: list[tuple[PipelineEvent, Callable[[Any], None]]]):
        """
        Esegue il workflow e restituisce gli eventi di stato e il risultato finale.
        """
        iterator = await workflow.arun(query, stream=True, stream_intermediate_steps=True)
        content = None
        current_active_step = None

        async for event in iterator:
            step_name = getattr(event, 'step_name', '')

            # 1. Chiama i listeners (per i log)
            for app_event, listener in events:
                if app_event.check_event(event.event, step_name):
                    listener(event)

            # 2. Restituisce gli aggiornamenti di stato per Gradio
            if event.event == WorkflowRunEvent.step_started.value:
                current_active_step = step_name
                if step_name == PipelineEvent.QUERY_CHECK.value:
                    yield "🔍 Sto controllando la tua richiesta..."
                elif step_name == PipelineEvent.INFO_RECOVERY.value:
                    yield "📊 Sto recuperando i dati (mercato, news, social)..."
                elif step_name == PipelineEvent.REPORT_GENERATION.value:
                    yield "✍️ Sto scrivendo il report finale..."

            # Gestisce gli eventi di tool promossi dal Team
            elif event.event == PipelineEvent.TOOL_USED.value:
                if current_active_step == PipelineEvent.INFO_RECOVERY.value:
                    tool_object = getattr(event, 'tool', None)
                    if tool_object:
                        tool_name = getattr(tool_object, 'tool_name', 'uno strumento sconosciuto')
                        user_message = _get_user_friendly_action(tool_name)
                        yield f"{user_message}"
                    else:
                        yield f"Sto usando uno strumento sconosciuto..."

            # 3. Salva il contenuto finale quando uno step è completato
            elif event.event == WorkflowRunEvent.step_completed.value:
                current_active_step = None
                content = getattr(event, 'content', '')

        # 4. Restituisce la risposta finale
        if content and isinstance(content, str):
            think_str = "</think>"
            think = content.rfind(think_str)
            final_answer = content[(think + len(think_str)):] if think != -1 else content
            yield final_answer
        elif content and isinstance(content, QueryOutputs):
            yield content.response
        else:
            logging.error(f"No output from workflow: {content}")
            yield "Nessun output dal workflow, qualcosa è andato storto."

# Funzione di utilità per messaggi user-friendly
def _get_user_friendly_action(tool_name: str) -> str:
    """
    Restituisce un messaggio leggibile e descrittivo per l'utente
    in base al nome dello strumento o funzione invocata.
    """
    descriptions = {
        # --- MarketAPIsTool ---
        "get_product": "🔍 Recupero le informazioni sul prodotto richiesto...",
        "get_products": "📦 Recupero i dati su più asset...",
        "get_historical_prices": "📊 Recupero i dati storici dei prezzi...",
        "get_products_aggregated": "🧩 Aggrego le informazioni da più fonti...",
        "get_historical_prices_aggregated": "📈 Creo uno storico aggregato dei prezzi...",

        # --- NewsAPIsTool (Aggiunto) ---
        "get_top_headlines": "📰 Cerco le notizie principali...",
        "get_latest_news": "🔎 Cerco notizie recenti su un argomento...",
        "get_top_headlines_aggregated": "🗞️ Raccolgo le notizie principali da tutte le fonti...",
        "get_latest_news_aggregated": "📚 Raccolgo notizie specifiche da tutte le fonti...",

        # --- SocialAPIsTool (Aggiunto) ---
        "get_top_crypto_posts": "📱 Cerco i post più popolari sui social...",
        "get_top_crypto_posts_aggregated": "🌐 Raccolgo i post da tutte le piattaforme social...",
    }

    # Messaggio di fallback generico
    return descriptions.get(tool_name, f"⚙️ Eseguo l'operazione: {tool_name}...")