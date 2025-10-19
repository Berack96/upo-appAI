from pydantic import BaseModel
from app.configs import AppConfig



class QueryInputs(BaseModel):
    user_query: str
    strategy: str

class QueryOutputs(BaseModel):
    response: str
    is_ok: bool



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
        self.leader_model = self.configs.models.all_models[index]

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





