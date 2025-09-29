from src.app.agents.news_agent import NewsAgent
from src.app.agents.social_agent import SocialAgent
from src.app.agents.predictor import PredictorStyle, PredictorInput, PredictorOutput, PREDICTOR_INSTRUCTIONS
from src.app.markets import MarketAPIs
from src.app.models import AppModels
from agno.utils.log import log_info

class ToolAgent:
    """
    Classe principale che coordina gli agenti per rispondere alle richieste dell'utente.
    """

    def __init__(self):
        """
        Inizializza l'agente con i modelli disponibili, gli stili e l'API di mercato.
        """
        self.social_agent = None
        self.news_agent = None
        self.predictor = None
        self.chosen_model = None
        self.available_models = AppModels.availables()
        self.all_styles = list(PredictorStyle)
        self.style = self.all_styles[0]  # Default to the first style

        self.market = MarketAPIs(currency="USD")
        self.choose_provider(0) # Default to the first model

    def choose_provider(self, index: int):
        """
        Sceglie il modello LLM da utilizzare in base all'indice fornito.

        Args:
            index: indice del modello nella lista available_models.
        """
        # TODO Utilizzare AGNO per gestire i modelli... è molto più semplice e permette di cambiare modello facilmente
        # TODO https://docs.agno.com/introduction
        # Inoltre permette di creare dei team e workflow di agenti più facilmente
        self.chosen_model = self.available_models[index]
        self.predictor = self.chosen_model.get_agent(PREDICTOR_INSTRUCTIONS, output=PredictorOutput)
        self.news_agent = NewsAgent()
        self.social_agent = SocialAgent()

    def choose_style(self, index: int):
        """
        Sceglie lo stile di previsione da utilizzare in base all'indice fornito.

        Args:
            index: indice dello stile nella lista all_styles.
        """
        self.style = self.all_styles[index]

    def interact(self, query: str) -> str:
        """
        Funzione principale che coordina gli agenti per rispondere alla richiesta dell'utente.

        Args:
            query: richiesta dell'utente (es. "Qual è la previsione per Bitcoin?")
        """

        log_info(f"[model={self.chosen_model.name}] [style={self.style.name}] [query=\"{query.replace('"', "'")}\"]")
        # TODO Step 0: ricerca e analisi della richiesta (es. estrazione di criptovalute specifiche)
        # Prendere la query dell'utente e fare un'analisi preliminare con una agente o con un team di agenti (social e news)

        # Step 1: raccolta analisi
        cryptos = ["BTC", "ETH", "XRP", "LTC", "BCH"]  # TODO rendere dinamico in futuro
        market_data = self.market.get_products(cryptos)
        news_sentiment = self.news_agent.analyze(query)
        social_sentiment = self.social_agent.analyze(query)
        log_info(f"End of data collection")

        # Step 2: aggrega sentiment
        sentiment = f"{news_sentiment}\n{social_sentiment}"

        # Step 3: previsione
        inputs = PredictorInput(data=market_data, style=self.style, sentiment=sentiment)
        result = self.predictor.run(inputs)
        prediction: PredictorOutput = result.content
        log_info(f"End of prediction")

        market_data = "\n".join([f"{product.symbol}: {product.price}" for product in market_data])
        output = f"[{prediction.strategy}]\nPortafoglio:\n" + "\n".join(
            [f"{item.asset} ({item.percentage}%): {item.motivation}" for item in prediction.portfolio]
        )

        return f"INPUT:\n{market_data}\n{sentiment}\n\n\nOUTPUT:\n{output}"

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
