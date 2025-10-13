import logging
from typing import Callable
from app.agents.prompts import *
from app.agents.team import AppTeam, AppEvent, TeamRunEvent, RunEvent
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
    def interact(self, query: str, listeners: dict[RunEvent | TeamRunEvent, Callable[[AppEvent], None]] = {}) -> str:
        """
        Esegue la pipeline di agenti per rispondere alla query dell'utente.
        1. Crea il Team di agenti.
        2. Aggiunge listener per eventi di logging.
        3. Esegue il Team con la query dell'utente.
        4. Recupera e restituisce l'output generato dagli agenti.
        Args:
            query (str): La query dell'utente.
        Returns:
            str: La risposta generata dagli agenti.
        """
        logging.info(f"Pipeline received query: {query}")

        # Step 1: Creazione Team
        team = AppTeam(self.configs, self.team_model, self.leader_model)

        # Step 2: Aggiunti listener per eventi
        for event_name, listener in listeners.items():
            team.add_listener(event_name, listener)

        # Step 3: Esecuzione Team
        # TODO migliorare prompt (?)
        query = f"The user query is: {query}\n\n They requested a {self.strategy.label} investment strategy."
        result = team.run_team(query)

        # Step 4: Recupero output
        logging.info(f"Team finished")
        return result
