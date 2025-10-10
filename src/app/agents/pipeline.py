from app.agents.models import AppModels
from app.agents.predictor import PREDICTOR_INSTRUCTIONS, PredictorOutput, PredictorStyle


class Pipeline:
    """
    Coordina gli agenti di servizio (Market, News, Social) e il Predictor finale.
    Il Team è orchestrato da qwen3:latest (Ollama), mentre il Predictor è dinamico
    e scelto dall'utente tramite i dropdown dell'interfaccia grafica.
    """

    def __init__(self):
        self.available_models = AppModels.availables()
        self.all_styles = list(PredictorStyle)

        self.style = self.all_styles[0]
        self.choose_predictor(0)  # Modello di default

    # ======================
    # Dropdown handlers
    # ======================
    def choose_predictor(self, index: int):
        """
        Sceglie il modello LLM da usare per il Predictor.
        """
        model = self.available_models[index]
        self.predictor = model.get_agent(
            PREDICTOR_INSTRUCTIONS,
            output_schema=PredictorOutput,
        )

    def choose_style(self, index: int):
        """
        Sceglie lo stile (conservativo/aggressivo) da usare per il Predictor.
        """
        self.style = self.all_styles[index]

    # ======================
    # Helpers
    # ======================
    def list_providers(self) -> list[str]:
        """
        Restituisce la lista dei nomi dei modelli disponibili.
        """
        return [model.name for model in self.available_models]

    def list_styles(self) -> list[str]:
        """
        Restituisce la lista degli stili di previsione disponibili.
        """
        return [style.value for style in self.all_styles]

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
        from app.agents import AppTeam
        from agno.agent import RunEvent
        team = AppTeam(AppModels.OLLAMA_QWEN_1B) # TODO rendere dinamico
        team.add_listener(RunEvent.tool_call_started, lambda e: print(f"Team tool call started: {e.agent_name}")) # type: ignore
        team.add_listener(RunEvent.tool_call_completed, lambda e: print(f"Team tool call completed: {e.agent_name}")) # type: ignore
        result = team.run_team(query)
        return result
