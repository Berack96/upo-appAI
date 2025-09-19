from .agents.market_agent import MarketAgent
from .agents.news_agent import NewsAgent
from .agents.social_agent import SocialAgent
from .agents.predictor_agent import PredictorAgent


class ToolAgent:
    def __init__(self):
        self.market_agent = MarketAgent()
        self.news_agent = NewsAgent()
        self.social_agent = SocialAgent()
        self.predictor_agent = PredictorAgent()

    def interact(self, query, provider="mock", style="conservative"):
        # Step 1: raccolta analisi
        market_data = self.market_agent.analyze(query)
        news_sentiment = self.news_agent.analyze(query)
        social_sentiment = self.social_agent.analyze(query)

        # Step 2: aggrega sentiment
        sentiment = f"{news_sentiment}\n{social_sentiment}"

        # Step 3: previsione
        prediction = self.predictor_agent.predict(
            data=market_data,
            sentiment=sentiment,
            style=style,
            provider=provider
        )

        return f"{market_data}\n{sentiment}\n\n📈 Consiglio finale:\n{prediction}"
