import logging
from app.agents.models import AppModels
from app.agents.team import create_team_with
from app.agents.predictor import PREDICTOR_INSTRUCTIONS, PredictorOutput, PredictorStyle

logging = logging.getLogger(__name__)


class Pipeline:
    """
    Coordina gli agenti di servizio (Market, News, Social) e il Predictor finale.
    Il Team è orchestrato da qwen3:latest (Ollama), mentre il Predictor è dinamico
    e scelto dall'utente tramite i dropdown dell'interfaccia grafica.
    """

    # Variabili statiche
    available_models = AppModels.availables()
    all_styles = list(PredictorStyle)

    def __init__(self):
        self.style = Pipeline.all_styles[0]
        self.team = create_team_with(AppModels.OLLAMA_QWEN_1B)
        self.choose_predictor(0)  # Modello di default

    # ======================
    # Dropdown handlers
    # ======================
    def choose_predictor(self, index: int):
        """
        Sceglie il modello LLM da usare per il Predictor.
        """
        model = Pipeline.available_models[index]
        self.predictor = model.get_agent(
            PREDICTOR_INSTRUCTIONS,
            output_schema=PredictorOutput,
        )

    def choose_style(self, index: int):
        """
        Sceglie lo stile (conservativo/aggressivo) da usare per il Predictor.
        """
        self.style = Pipeline.all_styles[index]

    # ======================
    # Helpers
    # ======================
    def list_providers(self) -> list[str]:
        """
        Restituisce la lista dei nomi dei modelli disponibili.
        """
        return [model.name for model in Pipeline.available_models]

    def list_styles(self) -> list[str]:
        """
        Restituisce la lista degli stili di previsione disponibili.
        """
        return [style.value for style in Pipeline.all_styles]

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
        logging.info(f"Pipeline received query: {query}")
        team_outputs = self.team.run(query) # type: ignore

        # Step 2: recupero ouput
        if not isinstance(team_outputs.content, str):
            logging.error(f"Team output is not a string: {team_outputs.content}")
            raise ValueError("Team output is not a string")
        logging.info(f"Team finished")
        return team_outputs.content
