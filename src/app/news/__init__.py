from agno.tools import Toolkit
from app.utils.wrapper_handler import WrapperHandler
from .base import NewsWrapper, Article
from .news_api import NewsApiWrapper
from .gnews_api import GoogleNewsWrapper
from .cryptopanic_api import CryptoPanicWrapper
from .duckduckgo import DuckDuckGoWrapper

__all__ = ["NewsAPIsTool", "NEWS_INSTRUCTIONS", "NewsApiWrapper", "GoogleNewsWrapper", "CryptoPanicWrapper", "DuckDuckGoWrapper"]


class NewsAPIsTool(NewsWrapper, Toolkit):
    """
    Aggregates multiple news API wrappers and manages them using WrapperHandler.
    This class supports retrieving top headlines and latest news articles by querying multiple sources:
    - GoogleNewsWrapper
    - DuckDuckGoWrapper
    - NewsApiWrapper
    - CryptoPanicWrapper

    By default, it returns results from the first successful wrapper. 
    Optionally, it can be configured to collect articles from all wrappers.
    If no wrapper succeeds, an exception is raised.
    """

    def __init__(self):
        wrappers = [GoogleNewsWrapper, DuckDuckGoWrapper, NewsApiWrapper, CryptoPanicWrapper]
        self.wrapper_handler: WrapperHandler[NewsWrapper] = WrapperHandler.build_wrappers(wrappers)

        Toolkit.__init__(
            self,
            name="News APIs Toolkit",
            tools=[
                self.get_top_headlines,
                self.get_latest_news,
            ],
        )

    # TODO Pensare se ha senso restituire gli articoli da TUTTI i wrapper o solo dal primo che funziona
    # la modifica è banale, basta usare try_call_all invece di try_call
    def get_top_headlines(self, total: int = 100) -> list[Article]:
        return self.wrapper_handler.try_call(lambda w: w.get_top_headlines(total))
    def get_latest_news(self, query: str, total: int = 100) -> list[Article]:
        return self.wrapper_handler.try_call(lambda w: w.get_latest_news(query, total))


# TODO migliorare il prompt
NEWS_INSTRUCTIONS = """
Utilizza questo strumento per ottenere le ultime notizie e i titoli principali relativi a criptovalute specifiche. Puoi richiedere le notizie più recenti o i titoli principali.

Esempio di utilizzo:
- get_latest_news("crypto", limit=5) # ottieni le ultime 5 notizie su "crypto", la query può essere qualsiasi argomento di interesse
- get_top_headlines(limit=3) # ottieni i 3 titoli principali delle notizie globali

"""
