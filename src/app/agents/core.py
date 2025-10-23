from pydantic import BaseModel
from agno.agent import Agent
from agno.team import Team
from agno.tools.reasoning import ReasoningTools
from app.agents.plan_memory_tool import PlanMemoryTool
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
        assert index >= 0 and index < len(self.configs.models.all_models), "Index out of range for models list."
        self.query_analyzer_model = self.configs.models.all_models[index]

    def choose_team_leader(self, index: int):
        """
        Sceglie il modello LLM da usare per il Team Leader.
        """
        assert index >= 0 and index < len(self.configs.models.all_models), "Index out of range for models list."
        self.team_leader_model = self.configs.models.all_models[index]

    def choose_team(self, index: int):
        """
        Sceglie il modello LLM da usare per il Team.
        """
        assert index >= 0 and index < len(self.configs.models.all_models), "Index out of range for models list."
        self.team_model = self.configs.models.all_models[index]

    def choose_report_generator(self, index: int):
        """
        Sceglie il modello LLM da usare per il generatore di report.
        """
        assert index >= 0 and index < len(self.configs.models.all_models), "Index out of range for models list."
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
        market, news, social = self.get_tools()
        market_agent = self.team_model.get_agent(MARKET_INSTRUCTIONS, "Market Agent", tools=[market])
        news_agent = self.team_model.get_agent(NEWS_INSTRUCTIONS, "News Agent", tools=[news])
        social_agent = self.team_model.get_agent(SOCIAL_INSTRUCTIONS, "Socials Agent", tools=[social])
        return Team(
            model=self.team_leader_model.get_model(TEAM_LEADER_INSTRUCTIONS),
            name="CryptoAnalysisTeam",
            tools=[ReasoningTools(), PlanMemoryTool(), CryptoSymbolsTools()],
            members=[market_agent, news_agent, social_agent],
        )

    def get_agent_query_checker(self) -> Agent:
        return self.query_analyzer_model.get_agent(QUERY_CHECK_INSTRUCTIONS, "Query Check Agent", output_schema=QueryOutputs)

    def get_agent_report_generator(self) -> Agent:
        return self.report_generation_model.get_agent(REPORT_GENERATION_INSTRUCTIONS, "Report Generator Agent")

    def get_tools(self) -> tuple[MarketAPIsTool, NewsAPIsTool, SocialAPIsTool]:
        """
        Restituisce la lista di tools disponibili per gli agenti.
        """
        api = self.configs.api

        market_tool = MarketAPIsTool()
        market_tool.handler.set_retries(api.retry_attempts, api.retry_delay_seconds)
        news_tool = NewsAPIsTool()
        news_tool.handler.set_retries(api.retry_attempts, api.retry_delay_seconds)
        social_tool = SocialAPIsTool()
        social_tool.handler.set_retries(api.retry_attempts, api.retry_delay_seconds)
        return market_tool, news_tool, social_tool

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
    def __init__(self, inputs: PipelineInputs, prefix: str = "", suffix: str = ""):
        self.base_message = f"Running configurations: \n{prefix}{inputs}{suffix}\n\n"
        self.emojis = ['🔳', '➡️', '✅']
        self.placeholder = '<<<>>>'
        self.current = 0
        self.steps_total = [
            (f"{self.placeholder} Query Check", 1),
            (f"{self.placeholder} Info Recovery", 0),
            (f"{self.placeholder} Report Generation", 0),
        ]

    def update(self) -> 'RunMessage':
        text_curr, state_curr = self.steps_total[self.current]
        self.steps_total[self.current] = (text_curr, state_curr + 1)
        self.current += 1
        if self.current < len(self.steps_total):
            text_curr, state_curr = self.steps_total[self.current]
            self.steps_total[self.current] = (text_curr, state_curr + 1)
        return self

    def get_latest(self, extra: str = "") -> str:
        steps = [msg.replace(self.placeholder, self.emojis[state]) for msg, state in self.steps_total]
        if extra:
            steps[self.current] = f"{steps[self.current]}: {extra}"
        return self.base_message + "\n".join(steps)
