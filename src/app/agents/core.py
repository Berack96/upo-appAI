from pydantic import BaseModel
from agno.agent import Agent
from agno.team import Team
from agno.tools.reasoning import ReasoningTools
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
    def choose_team_leader(self, index: int):
        """
        Sceglie il modello LLM da usare per il Team Leader.
        """
        self.team_leader_model = self.configs.models.all_models[index]

    def choose_team(self, index: int):
        """
        Sceglie il modello LLM da usare per il Team.
        """
        self.team_model = self.configs.models.all_models[index]

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
            tools=[ReasoningTools()],
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

        market_tool = MarketAPIsTool(currency=api.currency)
        market_tool.handler.set_retries(api.retry_attempts, api.retry_delay_seconds)
        news_tool = NewsAPIsTool()
        news_tool.handler.set_retries(api.retry_attempts, api.retry_delay_seconds)
        social_tool = SocialAPIsTool()
        social_tool.handler.set_retries(api.retry_attempts, api.retry_delay_seconds)
        return market_tool, news_tool, social_tool