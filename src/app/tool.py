from app.agents.market_agent import MarketAgent
from app.agents.news_agent import NewsAgent
from app.agents.social_agent import SocialAgent
from app.agents.predictor_agent import PredictorAgent
from app.models import Models


class ToolAgent:
    def __init__(self, available_models: list[Models]):
        self.market_agent = MarketAgent()
        self.news_agent = NewsAgent()
        self.social_agent = SocialAgent()
        self.predictor_agent = PredictorAgent()

    def interact(self, query: str, provider: str, style: str):
        """
        Funzione principale che coordina gli agenti per rispondere alla richiesta dell'utente.
        """
        # TODO Utilizzare AGNO per gestire i modelli... è molto più semplice e permette di cambiare modello facilmente
        # TODO https://docs.agno.com/introduction
        # Inoltre permette di creare dei team e workflow di agenti più facilmente

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
