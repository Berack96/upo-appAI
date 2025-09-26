from app.agents.news_agent import NewsAgent
from app.agents.social_agent import SocialAgent
from app.agents import predictor
from app.agents.predictor import PredictorStyle
from app.markets import get_first_available_market_api
from app.models import Models


class ToolAgent:
    """
    Classe principale che coordina gli agenti per rispondere alle richieste dell'utente.
    available_models: lista dei modelli disponibili (Models.availables()).
    all_styles: lista degli stili di previsione disponibili (PredictorStyle).
    """

    def __init__(self, available_models: list[Models], all_styles: list[PredictorStyle]):
        """
        Inizializza l'agente con i modelli e gli stili disponibili.
        """
        self.available_models = available_models
        self.all_styles = all_styles

        self.market = get_first_available_market_api(currency="USD")
        self.choose_provider(0) # Default to the first model

    def choose_provider(self, index: int):
        """
        Sceglie il modello LLM da utilizzare in base all'indice fornito.
        index: indice del modello nella lista available_models.
        """
        # TODO Utilizzare AGNO per gestire i modelli... è molto più semplice e permette di cambiare modello facilmente
        # TODO https://docs.agno.com/introduction
        # Inoltre permette di creare dei team e workflow di agenti più facilmente
        chosen_model = self.available_models[index]
        self.predictor = chosen_model.get_agent(predictor.instructions())
        self.news_agent = NewsAgent()
        self.social_agent = SocialAgent()

    def interact(self, query: str, style_index: int):
        """
        Funzione principale che coordina gli agenti per rispondere alla richiesta dell'utente.
        query: richiesta dell'utente (es. "Qual è la previsione per Bitcoin?")
        style_index: indice dello stile di previsione nella lista all_styles.
        """

        # Step 1: raccolta analisi
        cryptos = ["BTC", "ETH", "XRP", "LTC", "BCH"]  # TODO rendere dinamico in futuro
        market_data = self.market.get_products(cryptos)
        news_sentiment = self.news_agent.analyze(query)
        social_sentiment = self.social_agent.analyze(query)

        # Step 2: aggrega sentiment
        sentiment = f"{news_sentiment}\n{social_sentiment}"

        # Step 3: previsione
        inputs = predictor.prepare_inputs(
            data=market_data,
            style=self.all_styles[style_index],
            sentiment=sentiment
        )

        prediction = self.predictor.run(inputs)
        #output = prediction.content.split("</think>")[-1] # remove thinking steps and reasoning from the final output
        output = prediction.content

        market_data = "\n".join([f"{product.symbol}: {product.price}" for product in market_data])
        return f"{market_data}\n{sentiment}\n\n📈 Consiglio finale:\n{output}"
