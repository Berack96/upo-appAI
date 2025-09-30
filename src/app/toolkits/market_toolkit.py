from agno.tools import Toolkit
from app.markets import MarketAPIs


# TODO (?) in futuro fare in modo che la LLM faccia da sé per il mercato
# Non so se può essere utile, per ora lo lascio qui
# per ora mettiamo tutto statico e poi, se abbiamo API-Key senza limiti
# possiamo fare in modo di far scegliere alla LLM quale crypto proporre
# in base alle sue proprie chiamate API
class MarketToolkit(Toolkit):
    def __init__(self):
        self.market_api = MarketAPIs()

        super().__init__(
            name="Market Toolkit",
            tools=[
                self.market_api.get_historical_prices,
                self.market_api.get_product,
            ],
        )

def instructions():
    return """
    Utilizza questo strumento per ottenere dati di mercato storici e attuali per criptovalute specifiche.
    Puoi richiedere i prezzi storici o il prezzo attuale di una criptovaluta specifica.
    Esempio di utilizzo:
    - get_historical_prices("BTC", limit=10) # ottieni gli ultimi 10 prezzi storici di Bitcoin
    - get_product("ETH")
    """
