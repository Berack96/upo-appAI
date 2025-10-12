import logging
from app.agents.team import create_team_with
from app.agents.prompts import *
from app.configs import AppConfig

logging = logging.getLogger("pipeline")


class Pipeline:
    """
    Coordina gli agenti di servizio (Market, News, Social) e il Predictor finale.
    Il Team è orchestrato da qwen3:latest (Ollama), mentre il Predictor è dinamico
    e scelto dall'utente tramite i dropdown dell'interfaccia grafica.
    """

    def __init__(self, configs: AppConfig):
        self.configs = configs

        # Stato iniziale
        self.leader_model = self.configs.get_model_by_name(self.configs.agents.team_leader_model)
        self.team_model = self.configs.get_model_by_name(self.configs.agents.team_model)
        self.strategy = self.configs.get_strategy_by_name(self.configs.agents.strategy)

    # ======================
    # Dropdown handlers
    # ======================
    def choose_leader(self, index: int):
        """
        Sceglie il modello LLM da usare per il Team.
        """
        self.leader_model = self.configs.models.all_models[index]

    def choose_team(self, index: int):
        """
        Sceglie il modello LLM da usare per il Team.
        """
        self.team_model = self.configs.models.all_models[index]

    def choose_strategy(self, index: int):
        """
        Sceglie la strategia da usare per il Predictor.
        """
        self.strategy = self.configs.strategies[index]

    # ======================
    # Helpers
    # ======================
    def list_providers(self) -> list[str]:
        """
        Restituisce la lista dei nomi dei modelli disponibili.
        """
        return [model.label for model in self.configs.models.all_models]

    def list_styles(self) -> list[str]:
        """
        Restituisce la lista degli stili di previsione disponibili.
        """
        return [strat.label for strat in self.configs.strategies]

    # ======================
    # Core interaction
    # ======================
    def interact(self, query: str) -> str:
        """
        1. Raccoglie output dai membri del Team
        2. Aggrega output strutturati
        3. Invoca Predictor
        4. Restituisce la strategia finale
        """
        # Step 1: Creazione Team
        team = create_team_with(self.configs, self.team_model, self.leader_model)

        # Step 2: raccolta output dai membri del Team
        logging.info(f"Pipeline received query: {query}")
        # TODO migliorare prompt (?)
        query = f"The user query is: {query}\n\n They requested a {self.strategy.label} investment strategy."
        team_outputs = team.run(query) # type: ignore

        # Step 3: recupero ouput
        if not isinstance(team_outputs.content, str):
            logging.error(f"Team output is not a string: {team_outputs.content}")
            raise ValueError("Team output is not a string")
        logging.info(f"Team finished")
        return team_outputs.content
