from typing import Union, List, Dict, Optional, Any, Iterator, Sequence
from agno.agent import Agent
from agno.models.message import Message
from agno.run.agent import RunOutput, RunOutputEvent
from pydantic import BaseModel

from src.app.toolkits.market_toolkit import MarketToolkit
from src.app.markets.base import ProductInfo  # modello dati già definito nel tuo progetto


class MarketAgent(Agent):
    """
    Wrapper che trasforma MarketToolkit in un Agent compatibile con Team.
    Produce sia output leggibile (content) che dati strutturati (metadata).
    """

    def __init__(self, currency: str = "USD"):
        super().__init__()
        self.toolkit = MarketToolkit()
        self.currency = currency
        self.name = "MarketAgent"

    def run(
        self,
        input: Union[str, List, Dict, Message, BaseModel, List[Message]],
        *,
        stream: Optional[bool] = None,
        stream_intermediate_steps: Optional[bool] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        session_state: Optional[Dict[str, Any]] = None,
        audio: Optional[Sequence[Any]] = None,
        images: Optional[Sequence[Any]] = None,
        videos: Optional[Sequence[Any]] = None,
        files: Optional[Sequence[Any]] = None,
        retries: Optional[int] = None,
        knowledge_filters: Optional[Dict[str, Any]] = None,
        add_history_to_context: Optional[bool] = None,
        add_dependencies_to_context: Optional[bool] = None,
        add_session_state_to_context: Optional[bool] = None,
        dependencies: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        yield_run_response: bool = False,
        debug_mode: Optional[bool] = None,
        **kwargs: Any,
    ) -> Union[RunOutput, Iterator[Union[RunOutputEvent, RunOutput]]]:
        # 1. Estraggo la query dal parametro "input"
        if isinstance(input, str):
            query = input
        elif isinstance(input, dict) and "query" in input:
            query = input["query"]
        elif isinstance(input, Message):
            query = input.content
        elif isinstance(input, BaseModel):
            query = str(input)
        elif isinstance(input, list) and input and isinstance(input[0], Message):
            query = input[0].content
        else:
            query = str(input)

        # 2. Individuo i simboli da analizzare
        symbols = []
        for token in query.upper().split():
            if token in ("BTC", "ETH", "XRP", "LTC", "BCH"):  # TODO: estendere dinamicamente
                symbols.append(token)

        if not symbols:
            symbols = ["BTC", "ETH"]  # default

        # 3. Recupero i dati dal toolkit
        results = []
        products: List[ProductInfo] = []

        for sym in symbols:
            try:
                product = self.toolkit.get_current_price(sym)  # supponiamo ritorni un ProductInfo o simile
                if isinstance(product, list):
                    products.extend(product)
                else:
                    products.append(product)

                results.append(f"{sym}: {product.price if hasattr(product, 'price') else product}")
            except Exception as e:
                results.append(f"{sym}: errore ({e})")

        # 4. Preparo output leggibile + metadati strutturati
        output_text = "📊 Dati di mercato:\n" + "\n".join(results)

        return RunOutput(
            content=output_text,
            metadata={"products": products}
        )
