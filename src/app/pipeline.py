from agno.team import Team
from agno.utils.log import log_info

from app.news import NewsAPIsTool, NEWS_INSTRUCTIONS
from app.social import SocialAPIsTool, SOCIAL_INSTRUCTIONS
from app.markets import MarketAPIsTool, MARKET_INSTRUCTIONS
from app.models import AppModels
from app.predictor import PredictorStyle, PredictorInput, PredictorOutput, PREDICTOR_INSTRUCTIONS


class Pipeline:
    """
    Pipeline coordinata: esegue tutti gli agenti del Team, aggrega i risultati e invoca il Predictor.
    """

    def __init__(self):
        # Inizializza gli agenti
        market_agent = AppModels.OLLAMA_QWEN_1B.get_agent(
            instructions=MARKET_INSTRUCTIONS,
            name="MarketAgent",
            tools=[MarketAPIsTool()]
        )
        news_agent = AppModels.OLLAMA_QWEN_1B.get_agent(
            instructions=NEWS_INSTRUCTIONS,
            name="NewsAgent",
            tools=[NewsAPIsTool()]
        )
        social_agent = AppModels.OLLAMA_QWEN_1B.get_agent(
            instructions=SOCIAL_INSTRUCTIONS,
            name="SocialAgent",
            tools=[SocialAPIsTool()]
        )

        # Crea il Team
        prompt = """
        You are the coordinator of a team of analysts specialized in cryptocurrency market analysis.
        Your role is to gather insights from various sources, including market data, news articles, and social media trends.
        Based on the information provided by your team members, you will synthesize a comprehensive sentiment analysis for each cryptocurrency discussed.
        Your analysis should consider the following aspects:
        1. Market Trends: Evaluate the current market trends and price movements.
        2. News Impact: Assess the impact of recent news articles on market sentiment.
        3. Social Media Buzz: Analyze social media discussions and trends related to the cryptocurrencies.
        Your final output should be a well-rounded sentiment analysis that can guide investment decisions.
        """ # TODO migliorare il prompt
        self.team = Team(
            model = AppModels.OLLAMA_QWEN_1B.get_model(prompt),
            name="CryptoAnalysisTeam",
            members=[market_agent, news_agent, social_agent]
        )

        # Modelli disponibili e Predictor
        self.available_models = AppModels.availables()
        self.predictor_model = self.available_models[0]
        self.predictor = self.predictor_model.get_agent(PREDICTOR_INSTRUCTIONS, output=PredictorOutput) # type: ignore[arg-type]

        # Stili
        self.styles = list(PredictorStyle)
        self.style = self.styles[0]

    def choose_provider(self, index: int):
        self.predictor_model = self.available_models[index]
        self.predictor = self.predictor_model.get_agent(PREDICTOR_INSTRUCTIONS, output=PredictorOutput) # type: ignore[arg-type]

    def choose_style(self, index: int):
        self.style = self.styles[index]

    def interact(self, query: str) -> str:
        """
        Esegue il Team (Market + News + Social), aggrega i risultati e invoca il Predictor.
        """
        # Step 1: raccogli output del Team
        team_results = self.team.run(query)
        if isinstance(team_results, dict):  # alcuni Team possono restituire dict
            pieces = [str(v) for v in team_results.values()]
        elif isinstance(team_results, list):
            pieces = [str(r) for r in team_results]
        else:
            pieces = [str(team_results)]
        aggregated_text = "\n\n".join(pieces)

        # Step 2: prepara input per Predictor
        predictor_input = PredictorInput(
            data=[],  # TODO: mappare meglio i dati di mercato in ProductInfo
            style=self.style,
            sentiment=aggregated_text
        )

        # Step 3: chiama Predictor
        result = self.predictor.run(predictor_input)
        prediction: PredictorOutput = result.content

        # Step 4: formatta output finale
        portfolio_lines = "\n".join(
            [f"{item.asset} ({item.percentage}%): {item.motivation}" for item in prediction.portfolio]
        )
        output = (
            f"📊 Strategia ({self.style.value}): {prediction.strategy}\n\n"
            f"💼 Portafoglio consigliato:\n{portfolio_lines}"
        )

        return output

    def list_providers(self) -> list[str]:
        return [m.name for m in self.available_models]

    def list_styles(self) -> list[str]:
        return [s.value for s in self.styles]
