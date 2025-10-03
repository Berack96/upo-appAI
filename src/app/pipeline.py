from agno.run.agent import RunOutput
from agno.team import Team

from app.agents.market_agent import MarketAgent
from app.agents.news_agent import NewsAgent
from app.agents.social_agent import SocialAgent
from app.models import AppModels
from app.predictor import PredictorInput, PredictorOutput, PredictorStyle, PREDICTOR_INSTRUCTIONS


class Pipeline:
    """
    Coordina gli agenti di servizio (Market, News, Social) e il Predictor finale.
    Il Team è orchestrato da qwen3:latest (Ollama), mentre il Predictor è dinamico
    e scelto dall'utente tramite i dropdown dell'interfaccia grafica.
    """
    def __init__(self):
        # === Membri del team ===
        self.market_agent = MarketAgent()
        self.news_agent = NewsAgent()
        self.social_agent = SocialAgent()

        # === Modello di orchestrazione del Team ===
        team_model = AppModels.OLLAMA_QWEN.get_model(
            # TODO: migliorare le istruzioni del team
            "Agisci come coordinatore: smista le richieste tra MarketAgent, NewsAgent e SocialAgent."
        )

        # === Team ===
        self.team = Team(
            name="CryptoAnalysisTeam",
            members=[self.market_agent, self.news_agent, self.social_agent],
            model=team_model
        )

        # === Predictor ===
        self.available_models = AppModels.availables()
        self.all_styles = list(PredictorStyle)

        # Scelte di default
        self.chosen_model = self.available_models[0] if self.available_models else None
        self.style = self.all_styles[0] if self.all_styles else None

        self._init_predictor() # Inizializza il predictor con il modello di default

    # ======================
    # Dropdown handlers
    # ======================
    def choose_provider(self, index: int):
        """
        Sceglie il modello LLM da usare per il Predictor.
        """
        self.chosen_model = self.available_models[index]
        self._init_predictor()

    def choose_style(self, index: int):
        """
        Sceglie lo stile (conservativo/aggressivo) da usare per il Predictor.
        """
        self.style = self.all_styles[index]

    # ======================
    # Helpers
    # ======================
    def _init_predictor(self):
        """
        Inizializza (o reinizializza) il Predictor in base al modello scelto.
        """
        if not self.chosen_model:
            return
        self.predictor = self.chosen_model.get_agent(
            PREDICTOR_INSTRUCTIONS,
            output=PredictorOutput, # type: ignore
        )

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
        if not self.predictor or not self.style:
            return "⚠️ Devi prima selezionare un modello e una strategia validi dagli appositi menu."

        # Step 1: raccolta output dai membri del Team
        team_outputs = self.team.run(query)

        # Step 2: aggregazione output strutturati
        all_products = []
        sentiments = []

        for agent_output in team_outputs.member_responses:
            if isinstance(agent_output, RunOutput):
                if "products" in agent_output.metadata:
                    all_products.extend(agent_output.metadata["products"])
                if "sentiment_news" in agent_output.metadata:
                    sentiments.append(agent_output.metadata["sentiment_news"])
                if "sentiment_social" in agent_output.metadata:
                    sentiments.append(agent_output.metadata["sentiment_social"])

        aggregated_sentiment = "\n".join(sentiments)

        # Step 3: invocazione Predictor
        predictor_input = PredictorInput(
            data=all_products,
            style=self.style,
            sentiment=aggregated_sentiment
        )

        result = self.predictor.run(predictor_input)
        prediction: PredictorOutput = result.content

        # Step 4: restituzione strategia finale
        portfolio_lines = "\n".join(
            [f"{item.asset} ({item.percentage}%): {item.motivation}" for item in prediction.portfolio]
        )
        return (
            f"📊 Strategia ({self.style.value}): {prediction.strategy}\n\n"
            f"💼 Portafoglio consigliato:\n{portfolio_lines}"
        )
