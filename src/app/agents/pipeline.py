from agno.run.agent import RunOutput
from app.agents.models import AppModels
from app.agents.team import create_team_with
from app.agents.predictor import PredictorInput, PredictorOutput, PredictorStyle
from app.agents.prompts import *
from app.api.base.markets import ProductInfo


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
        self.team = create_team_with(AppModels.OLLAMA_QWEN_1B)
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
        team_outputs = self.team.run(query) # type: ignore

        # Step 2: aggregazione output strutturati
        all_products: list[ProductInfo] = []
        sentiments: list[str] = []

        for agent_output in team_outputs.member_responses:
            if isinstance(agent_output, RunOutput) and agent_output.metadata is not None:
                keys = agent_output.metadata.keys()
                if "products" in keys:
                    all_products.extend(agent_output.metadata["products"])
                if "sentiment_news" in keys:
                    sentiments.append(agent_output.metadata["sentiment_news"])
                if "sentiment_social" in keys:
                    sentiments.append(agent_output.metadata["sentiment_social"])

        aggregated_sentiment = "\n".join(sentiments)

        # Step 3: invocazione Predictor
        predictor_input = PredictorInput(
            data=all_products,
            style=self.style,
            sentiment=aggregated_sentiment
        )

        result = self.predictor.run(predictor_input) # type: ignore
        if not isinstance(result.content, PredictorOutput):
            return "❌ Errore: il modello non ha restituito un output valido."
        prediction: PredictorOutput = result.content

        # Step 4: restituzione strategia finale
        portfolio_lines = "\n".join(
            [f"{item.asset} ({item.percentage}%): {item.motivation}" for item in prediction.portfolio]
        )
        return (
            f"📊 Strategia ({self.style.value}): {prediction.strategy}\n\n"
            f"💼 Portafoglio consigliato:\n{portfolio_lines}"
        )
