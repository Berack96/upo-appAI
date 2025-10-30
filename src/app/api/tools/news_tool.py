from agno.tools import Toolkit

from app.agents.action_registry import register_friendly_actions
from app.api.wrapper_handler import WrapperHandler
from app.api.core.news import NewsWrapper, Article
from app.api.news import NewsApiWrapper, GoogleNewsWrapper, CryptoPanicWrapper, DuckDuckGoWrapper
from app.configs import AppConfig

class NewsAPIsTool(NewsWrapper, Toolkit):
    """
    Aggregates multiple news API wrappers and manages them using WrapperHandler.
    This class supports retrieving top headlines and latest news articles by querying multiple sources.
    Providers can be configured in configs.yaml under api.news_providers.

    By default, it returns results from the first successful wrapper. 
    Optionally, it can be configured to collect articles from all wrappers.
    If no wrapper succeeds, an exception is raised.
    """

    def __init__(self):
        """
        Initialize the NewsAPIsTool with news API wrappers configured in configs.yaml.
        The order of wrappers is determined by the api.news_providers list in the configuration.
        """
        config = AppConfig()

        self.handler = WrapperHandler.build_wrappers(
            constructors=[NewsApiWrapper, GoogleNewsWrapper, CryptoPanicWrapper, DuckDuckGoWrapper],
            filters=config.api.news_providers,
            try_per_wrapper=config.api.retry_attempts,
            retry_delay=config.api.retry_delay_seconds
        )

        Toolkit.__init__( # type: ignore
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
        """
        Retrieves top headlines from the *first available* news provider.

        This method sequentially queries multiple sources (e.g., Google, DuckDuckGo)
        and returns results from the first one that responds successfully.
        Use this for a fast, general overview of the news.

        Args:
            limit (int): The maximum number of articles to retrieve. Defaults to 100.

        Returns:
            list[Article]: A list of Article objects from the single successful provider.
        """
        return self.handler.try_call(lambda w: w.get_top_headlines(limit))

    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        """
        Searches for the latest news on a specific topic from the *first available* provider.

        This method sequentially queries multiple sources using the query
        and returns results from the first one that responds successfully.
        Use this for a fast, specific search.

        Args:
            query (str): The search topic to find relevant articles.
            limit (int): The maximum number of articles to retrieve. Defaults to 100.

        Returns:
            list[Article]: A list of Article objects from the single successful provider.
        """
        return self.handler.try_call(lambda w: w.get_latest_news(query, limit))

    def get_top_headlines_aggregated(self, limit: int = 100) -> dict[str, list[Article]]:
        """
        Retrieves top headlines from *all available providers* and aggregates the results.

        This method queries all configured sources and returns a dictionary
        mapping each provider's name to its list of articles.
        Use this when you need a comprehensive report or to compare sources.

        Args:
            limit (int): The maximum number of articles to retrieve *from each* provider. Defaults to 100.

        Returns:
            dict[str, list[Article]]: A dictionary mapping provider names (str) to their list of Articles.

        Raises:
            Exception: If all providers fail to return results.
        """
        return self.handler.try_call_all(lambda w: w.get_top_headlines(limit))

    def get_latest_news_aggregated(self, query: str, limit: int = 100) -> dict[str, list[Article]]:
        """
        Searches for news on a specific topic from *all available providers* and aggregates the results.

        This method queries all configured sources using the query and returns a dictionary
        mapping each provider's name to its list of articles.
        Use this when you need a comprehensive report or to compare sources.

        Args:
            query (str): The search topic to find relevant articles.
            limit (int): The maximum number of articles to retrieve *from each* provider. Defaults to 100.

        Returns:
            dict[str, list[Article]]: A dictionary mapping provider names (str) to their list of Articles.

        Raises:
            Exception: If all providers fail to return results.
        """
        return self.handler.try_call_all(lambda w: w.get_latest_news(query, limit))

register_friendly_actions({
    "get_top_headlines": "📰 Cerco le notizie principali...",
    "get_latest_news": "🔎 Cerco notizie recenti su un argomento...",
    "get_top_headlines_aggregated": "🗞️ Raccolgo le notizie principali da tutte le fonti...",
    "get_latest_news_aggregated": "📚 Raccolgo notizie specifiche da tutte le fonti...",
})