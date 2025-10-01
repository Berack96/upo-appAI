from agno.tools import Toolkit
from app.utils.wrapper_handler import WrapperHandler
from app.utils.market_aggregation import aggregate_product_info, aggregate_history_prices
from .base import BaseWrapper, ProductInfo, Price
from .coinbase import CoinBaseWrapper
from .binance import BinanceWrapper
from .cryptocompare import CryptoCompareWrapper
from .yfinance import YFinanceWrapper

__all__ = [ "MarketAPIs", "BinanceWrapper", "CoinBaseWrapper", "CryptoCompareWrapper", "YFinanceWrapper" ]


class MarketAPIsTool(BaseWrapper, Toolkit):
    """
    Class that aggregates multiple market API wrappers and manages them using WrapperHandler.
    This class supports retrieving product information and historical prices.
    This class can also aggregate data from multiple sources to provide a more comprehensive view of the market.
    The following wrappers are included in this order:
    - BinanceWrapper
    - YFinanceWrapper
    - CoinBaseWrapper
    - CryptoCompareWrapper
    """

    def __init__(self, currency: str = "USD"):
        """
        Initialize the MarketAPIsTool with multiple market API wrappers.
        The following wrappers are included in this order:
        - BinanceWrapper
        - YFinanceWrapper
        - CoinBaseWrapper
        - CryptoCompareWrapper
        Args:
            currency (str): Valuta in cui restituire i prezzi. Default è "USD".
        """
        kwargs = {"currency": currency or "USD"}
        wrappers = [ BinanceWrapper, YFinanceWrapper, CoinBaseWrapper, CryptoCompareWrapper ]
        self.wrappers: WrapperHandler[BaseWrapper] = WrapperHandler.build_wrappers(wrappers, kwargs=kwargs)

        Toolkit.__init__(
            self,
            name="Market APIs Toolkit",
            tools=[
                self.get_product,
                self.get_products,
                self.get_historical_prices,
                self.get_products_aggregated,
                self.get_historical_prices_aggregated,
            ],
        )

    def get_product(self, asset_id: str) -> ProductInfo:
        return self.wrappers.try_call(lambda w: w.get_product(asset_id))
    def get_products(self, asset_ids: list[str]) -> list[ProductInfo]:
        return self.wrappers.try_call(lambda w: w.get_products(asset_ids))
    def get_historical_prices(self, asset_id: str = "BTC", limit: int = 100) -> list[Price]:
        return self.wrappers.try_call(lambda w: w.get_historical_prices(asset_id, limit))


    def get_products_aggregated(self, asset_ids: list[str]) -> list[ProductInfo]:
        """
        Restituisce i dati aggregati per una lista di asset_id.\n
        Attenzione che si usano tutte le fonti, quindi potrebbe usare molte chiamate API (che potrebbero essere a pagamento).
        Args:
            asset_ids (list[str]): Lista di asset_id da cercare.
        Returns:
            list[ProductInfo]: Lista di ProductInfo aggregati.
        """
        all_products = self.wrappers.try_call_all(lambda w: w.get_products(asset_ids))
        return aggregate_product_info(all_products)

    def get_historical_prices_aggregated(self, asset_id: str = "BTC", limit: int = 100) -> list[Price]:
        """
        Restituisce i dati storici aggregati per un asset_id. Usa i dati di tutte le fonti disponibili e li aggrega.\n
        Attenzione che si usano tutte le fonti, quindi potrebbe usare molte chiamate API (che potrebbero essere a pagamento).
        Args:
            asset_id (str): Asset ID da cercare.
            limit (int): Numero massimo di dati storici da restituire.
        Returns:
            list[Price]: Lista di Price aggregati.
        """
        all_prices = self.wrappers.try_call_all(lambda w: w.get_historical_prices(asset_id, limit))
        return aggregate_history_prices(all_prices)

MARKET_INSTRUCTIONS = """
**TASK:** You are a specialized **Crypto Price Data Retrieval Agent**. Your primary goal is to fetch the most recent and/or historical price data for requested cryptocurrency assets (e.g., 'BTC', 'ETH', 'SOL'). You must provide the data in a clear and structured format.

**AVAILABLE TOOLS:**
1.  `get_products(asset_ids: list[str])`: Get **current** product/price info for a list of assets. **(PREFERITA: usa questa per i prezzi live)**
2.  `get_historical_prices(asset_id: str, limit: int)`: Get historical price data for one asset. Default limit is 100. **(PREFERITA: usa questa per i dati storici)**
3.  `get_products_aggregated(asset_ids: list[str])`: Get **aggregated current** product/price info for a list of assets. **(USA SOLO SE richiesto 'aggregato' o se `get_products` fallisce)**
4.  `get_historical_prices_aggregated(asset_id: str, limit: int)`: Get **aggregated historical** price data for one asset. **(USA SOLO SE richiesto 'aggregato' o se `get_historical_prices` fallisce)**

**USAGE GUIDELINE:**
* **Asset ID:** Always convert common names (e.g., 'Bitcoin', 'Ethereum') into their official ticker/ID (e.g., 'BTC', 'ETH').
* **Cost Management (Cruciale per LLM locale):**
    * **Priorità Bassa per Aggregazione:** **Non** usare i metodi `*aggregated` a meno che l'utente non lo richieda esplicitamente o se i metodi non-aggregati falliscono.
    * **Limitazione Storica:** Il limite predefinito per i dati storici deve essere **20** punti dati, a meno che l'utente non specifichi un limite diverso.
* **Fallimento Tool:** Se lo strumento non restituisce dati per un asset specifico, rispondi per quell'asset con: "Dati di prezzo non trovati per [Asset ID]."

**REPORTING REQUIREMENT:**
1.  **Format:** Output the results in a clear, easy-to-read list or table.
2.  **Live Price Request:** If an asset's *current price* is requested, report the **Asset ID**, **Latest Price**, and **Time/Date of the price**.
3.  **Historical Price Request:** If *historical data* is requested, report the **Asset ID**, the **Limit** of points returned, and the **First** and **Last** entries from the list of historical prices (Date, Price). Non stampare l'intera lista di dati storici.
4.  **Output:** For all requests, fornire un **unico e conciso riepilogo** dei dati reperiti.
"""