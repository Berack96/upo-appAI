from agno.run.agent import RunEvent
from app.agents.prompts import *
from app.agents.team import AppTeam
from app.configs import AppConfig


class Pipeline:
    """
    Coordina gli agenti di servizio (Market, News, Social) e il Predictor finale.
    Il Team è orchestrato da qwen3:latest (Ollama), mentre il Predictor è dinamico
    e scelto dall'utente tramite i dropdown dell'interfaccia grafica.
    """

    def __init__(self, configs: AppConfig):
        self.configs = configs

        # Stato iniziale
        self.choose_strategy(0)
        self.choose_predictor(0)

    # ======================
    # Dropdown handlers
    # ======================
    def choose_predictor(self, index: int):
        """
        Sceglie il modello LLM da usare per il Predictor.
        """
        self.predictor = self.configs.models.all_models[index]

    def choose_strategy(self, index: int):
        """
        Sceglie la strategia da usare per il Predictor.
        """
        self.strat = self.configs.strategies[index].description

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
        # Step 1: raccolta output dai membri del Team
        team = AppTeam(configs=self.configs, team_models=self.predictor)
        team.add_listener(RunEvent.tool_call_started, lambda e: print(f"Team tool call started: {e.agent_name}")) # type: ignore
        team.add_listener(RunEvent.tool_call_completed, lambda e: print(f"Team tool call completed: {e.agent_name}")) # type: ignore
        result = team.run_team(query)
        return result
