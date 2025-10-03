from agno.tools import Toolkit
from app.utils.wrapper_handler import WrapperHandler
from app.news.base import NewsWrapper, Article
from app.news.news_api import NewsApiWrapper
from app.news.googlenews import GoogleNewsWrapper
from app.news.cryptopanic_api import CryptoPanicWrapper
from app.news.duckduckgo import DuckDuckGoWrapper

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
                self.get_top_headlines_aggregated,
                self.get_latest_news_aggregated,
            ],
        )

    def get_top_headlines(self, limit: int = 100) -> list[Article]:
        return self.wrapper_handler.try_call(lambda w: w.get_top_headlines(limit))
    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        return self.wrapper_handler.try_call(lambda w: w.get_latest_news(query, limit))

    def get_top_headlines_aggregated(self, limit: int = 100) -> dict[str, list[Article]]:
        """
        Calls get_top_headlines on all wrappers/providers and returns a dictionary mapping their names to their articles.
        Args:
            limit (int): Maximum number of articles to retrieve from each provider.
        Returns:
            dict[str, list[Article]]: A dictionary mapping providers names to their list of Articles
        """
        return self.wrapper_handler.try_call_all(lambda w: w.get_top_headlines(limit))

    def get_latest_news_aggregated(self, query: str, limit: int = 100) -> dict[str, list[Article]]:
        """
        Calls get_latest_news on all wrappers/providers and returns a dictionary mapping their names to their articles.
        Args:
            query (str): The search query to find relevant news articles.
            limit (int): Maximum number of articles to retrieve from each provider.
        Returns:
            dict[str, list[Article]]: A dictionary mapping providers names to their list of Articles
        """
        return self.wrapper_handler.try_call_all(lambda w: w.get_latest_news(query, limit))


NEWS_INSTRUCTIONS = """
**TASK:** You are a specialized **Crypto News Analyst**. Your goal is to fetch the latest news or top headlines related to cryptocurrencies, and then **analyze the sentiment** of the content to provide a concise report to the team leader. Prioritize 'crypto' or specific cryptocurrency names (e.g., 'Bitcoin', 'Ethereum') in your searches.

**AVAILABLE TOOLS:**
1.  `get_latest_news(query: str, limit: int)`: Get the 'limit' most recent news articles for a specific 'query'.
2.  `get_top_headlines(limit: int)`: Get the 'limit' top global news headlines.
3.  `get_latest_news_aggregated(query: str, limit: int)`: Get aggregated latest news articles for a specific 'query'.
4.  `get_top_headlines_aggregated(limit: int)`: Get aggregated top global news headlines.

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
