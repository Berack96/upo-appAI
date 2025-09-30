
from agno.agent import Agent
from src.app.toolkits.market_toolkit import MarketToolkit


class MarketAgent(Agent):
    """
    Wrapper che trasforma MarketToolkit in un Agent compatibile con Team.
    Espone un metodo run(query) che restituisce dati di mercato.
    """

    def __init__(self, currency: str = "USD"):
        self.toolkit = MarketToolkit()
        self.currency = currency
        self.name = "MarketAgent"

    def run(self, query: str) -> str:
        # Heuristica semplice: se la query cita simboli specifici, recupera quelli
        symbols = []
        for token in query.upper().split():
            if token in ("BTC", "ETH", "XRP", "LTC", "BCH"):  # TODO: estendere dinamicamente
                symbols.append(token)

        if not symbols:
            symbols = ["BTC", "ETH"]  # default

        results = []
        for sym in symbols:
            try:
                price = self.toolkit.get_current_price(sym)
                results.append(f"{sym}: {price}")
            except Exception as e:
                results.append(f"{sym}: errore ({e})")

        return "📊 Dati di mercato:\n" + "\n".join(results)