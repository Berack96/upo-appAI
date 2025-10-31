from pydantic import BaseModel
from agno.agent import Agent
from agno.team import Team
from agno.tools.reasoning import ReasoningTools
from app.api.tools.plan_memory_tool import PlanMemoryTool
from app.api.tools import *
from app.configs import AppConfig
from app.agents.prompts import *



class QueryInputs(BaseModel):
    user_query: str
    strategy: str

class QueryOutputs(BaseModel):
    response: str
    is_crypto: bool

class PipelineInputs:
    """
    Classe necessaria per passare gli input alla Pipeline.
    Serve per raggruppare i parametri e semplificare l'inizializzazione.
    """

    def __init__(self, configs: AppConfig | None = None) -> None:
        """
        Inputs per la Pipeline di agenti.
        Setta i valori di default se non specificati.
        """
        self.configs = configs if configs else AppConfig()

        agents = self.configs.agents
        self.team_model = self.configs.get_model_by_name(agents.team_model)
        self.team_leader_model = self.configs.get_model_by_name(agents.team_leader_model)
        self.query_analyzer_model = self.configs.get_model_by_name(agents.query_analyzer_model)
        self.report_generation_model = self.configs.get_model_by_name(agents.report_generation_model)
        self.strategy = self.configs.get_strategy_by_name(agents.strategy)
        self.user_query = ""

    # ======================
    # Dropdown handlers
    # ======================
    def choose_query_checker(self, index: int):
        """
        Sceglie il modello LLM da usare per l'analizzatore di query.
        """
        assert 0 <= index < len(self.configs.models.all_models), "Index out of range for models list."
        self.query_analyzer_model = self.configs.models.all_models[index]

    def choose_team_leader(self, index: int):
        """
        Sceglie il modello LLM da usare per il Team Leader.
        """
        assert 0 <= index < len(self.configs.models.all_models), "Index out of range for models list."
        self.team_leader_model = self.configs.models.all_models[index]

    def choose_team(self, index: int):
        """
        Sceglie il modello LLM da usare per il Team.
        """
        assert 0 <= index < len(self.configs.models.all_models), "Index out of range for models list."
        self.team_model = self.configs.models.all_models[index]

    def choose_report_generator(self, index: int):
        """
        Sceglie il modello LLM da usare per il generatore di report.
        """
        assert 0 <= index < len(self.configs.models.all_models), "Index out of range for models list."
        self.report_generation_model = self.configs.models.all_models[index]

    def choose_strategy(self, index: int):
        """
        Sceglie la strategia da usare per il Team.
        """
        self.strategy = self.configs.strategies[index]

    # ======================
    # Helpers
    # ======================
    def list_models_names(self) -> list[str]:
        """
        Restituisce la lista dei nomi dei modelli disponibili.
        """
        return [model.label for model in self.configs.models.all_models]

    def list_strategies_names(self) -> list[str]:
        """
        Restituisce la lista delle strategie disponibili.
        """
        return [strat.label for strat in self.configs.strategies]

    def get_query_inputs(self) -> QueryInputs:
        """
        Restituisce gli input per l'agente di verifica della query.
        """
        return QueryInputs(
            user_query=self.user_query,
            strategy=self.strategy.label,
        )

    # ======================
    # Agent getters
    # ======================
    def get_agent_team(self) -> Team:
        market_agent = self.team_model.get_agent(MARKET_INSTRUCTIONS, "Market Agent", tools=[MarketAPIsTool()])
        news_agent = self.team_model.get_agent(NEWS_INSTRUCTIONS, "News Agent", tools=[NewsAPIsTool()])
        social_agent = self.team_model.get_agent(SOCIAL_INSTRUCTIONS, "Socials Agent", tools=[SocialAPIsTool()])
        return Team(
            model=self.team_leader_model.get_model(TEAM_LEADER_INSTRUCTIONS),
            name="CryptoAnalysisTeam",
            tools=[ReasoningTools(), PlanMemoryTool(), CryptoSymbolsTools()],
            members=[market_agent, news_agent, social_agent],
            stream_intermediate_steps=True
        )

    def get_agent_query_checker(self) -> Agent:
        return self.query_analyzer_model.get_agent(QUERY_CHECK_INSTRUCTIONS, "Query Check Agent", output_schema=QueryOutputs)

    def get_agent_report_generator(self) -> Agent:
        return self.report_generation_model.get_agent(REPORT_GENERATION_INSTRUCTIONS, "Report Generator Agent")

    def __str__(self) -> str:
        return "\n".join([
            f"Query Check:  {self.query_analyzer_model.label}",
            f"Team Leader:  {self.team_leader_model.label}",
            f"Team:         {self.team_model.label}",
            f"Report:       {self.report_generation_model.label}",
            f"Strategy:     {self.strategy.label}",
            f"User Query:   \"{self.user_query}\"",
        ])


class RunMessage:
    """
    Classe per gestire i messaggi di stato durante l'esecuzione della pipeline.
    Inizializza il messaggio con gli step e aggiorna lo stato, permettendo di ottenere
    il messaggio più recente da inviare all'utente.
    """

    def __init__(self, inputs: PipelineInputs, prefix: str = "", suffix: str = ""):
        """
        Inizializza il messaggio di esecuzione con gli step iniziali.
        Tre stati possibili per ogni step:
        - In corso (🔳)
        - In esecuzione (➡️)
        - Completato (✅)

        Lo stato di esecuzione può essere assegnato solo a uno step alla volta.
        Args:
            inputs (PipelineInputs): Input della pipeline per mostrare la configurazione
            prefix (str, optional): Prefisso del messaggio. Defaults to ""
            suffix (str, optional): Suffisso del messaggio. Defaults to ""
        """
        self.current = None
        self.steps_total = None
        self.base_message = f"Running configurations: \n{prefix}{inputs}{suffix}\n\n"
        self.emojis = ['🔳', '➡️', '✅']
        self.placeholder = '<<<>>>'
        self.set_steps(["Query Check", "Info Recovery", "Report Generation"])

    def set_steps(self, steps: list[str]) -> 'RunMessage':
        """
        Inizializza gli step di esecuzione con lo stato iniziale.
        Args:
            steps (list[str]): Lista degli step da includere nel messaggio.
        Returns:
            RunMessage: L'istanza aggiornata di RunMessage.
        """
        self.steps_total = [(f"{self.placeholder} {step}", 0) for step in steps]
        self.steps_total[0] = (self.steps_total[0][0], 1)  # Primo step in esecuzione
        self.current = 0
        return self

    def update(self) -> 'RunMessage':
        """
        Sposta lo stato di esecuzione al passo successivo.
        Lo step precedente completato viene marcato come completato.
        Returns:
            RunMessage: L'istanza aggiornata di RunMessage.
        """
        text_curr, state_curr = self.steps_total[self.current]
        self.steps_total[self.current] = (text_curr, state_curr + 1)
        self.current = min(self.current + 1, len(self.steps_total))
        if self.current < len(self.steps_total):
            text_curr, state_curr = self.steps_total[self.current]
            self.steps_total[self.current] = (text_curr, state_curr + 1)
        return self

    def update_step_with_tool(self, tool_used: str = "") -> 'RunMessage':
        """
        Aggiorna il messaggio per lo step corrente.
        Args:
            tool_used (str, optional): Testo aggiuntivo da includere nello step. Defaults to "".
        """
        text_curr, state_curr = self.steps_total[self.current]
        if tool_used:
            text_curr = f"{text_curr.replace('╚', '╠')}\n╚═ {tool_used}"
        self.steps_total[self.current] = (text_curr, state_curr)
        return self

    def get_latest(self) -> str:
        """
        Restituisce il messaggio di esecuzione più recente.
        Returns:
            str: Messaggio di esecuzione aggiornato.
        """
        steps = [msg.replace(self.placeholder, self.emojis[state]) for msg, state in self.steps_total]
        return self.base_message + "\n".join(steps)

