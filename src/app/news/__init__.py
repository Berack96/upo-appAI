from agno.tools import Toolkit
from app.utils.wrapper_handler import WrapperHandler
from .base import NewsWrapper, Article
from .news_api import NewsApiWrapper
from .googlenews import GoogleNewsWrapper
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
        """
        Initialize the NewsAPIsTool with multiple news API wrappers.
        The tool uses WrapperHandler to manage and invoke the different news API wrappers.
        The following wrappers are included in this order:
        - GoogleNewsWrapper.
        - DuckDuckGoWrapper.
        - NewsApiWrapper.
        - CryptoPanicWrapper.
        """
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


NEWS_INSTRUCTIONS = """
**TASK:** You are a specialized **Crypto News Analyst**. Your goal is to fetch the latest news or top headlines related to cryptocurrencies, and then **analyze the sentiment** of the content to provide a concise report to the team leader. Prioritize 'crypto' or specific cryptocurrency names (e.g., 'Bitcoin', 'Ethereum') in your searches.

**AVAILABLE TOOLS:**
1.  `get_latest_news(query: str, limit: int)`: Get the 'limit' most recent news articles for a specific 'query'.
2.  `get_top_headlines(limit: int)`: Get the 'limit' top global news headlines.

**USAGE GUIDELINE:**
* Always use `get_latest_news` with a relevant crypto-related query first.
* The default limit for news items should be 5 unless specified otherwise.
* If the tool doesn't return any articles, respond with "No relevant news articles found."

**REPORTING REQUIREMENT:**
1.  **Analyze** the tone and key themes of the retrieved articles.
2.  **Summarize** the overall **market sentiment** (e.g., highly positive, cautiously neutral, generally negative) based on the content.
3.  **Identify** the top 2-3 **main topics** discussed (e.g., new regulation, price surge, institutional adoption).
4.  **Output** a single, brief report summarizing these findings. Do not output the raw articles.
"""
