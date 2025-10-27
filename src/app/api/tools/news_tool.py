from agno.tools import Toolkit
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
        return self.handler.try_call(lambda w: w.get_top_headlines(limit))
    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        return self.handler.try_call(lambda w: w.get_latest_news(query, limit))

    def get_top_headlines_aggregated(self, limit: int = 100) -> dict[str, list[Article]]:
        """
        Calls get_top_headlines on all wrappers/providers and returns a dictionary mapping their names to their articles.
        Args:
            limit (int): Maximum number of articles to retrieve from each provider.
        Returns:
            dict[str, list[Article]]: A dictionary mapping providers names to their list of Articles
        Raises:
            Exception: If all wrappers fail to provide results.
        """
        return self.handler.try_call_all(lambda w: w.get_top_headlines(limit))

    def get_latest_news_aggregated(self, query: str, limit: int = 100) -> dict[str, list[Article]]:
        """
        Calls get_latest_news on all wrappers/providers and returns a dictionary mapping their names to their articles.
        Args:
            query (str): The search query to find relevant news articles.
            limit (int): Maximum number of articles to retrieve from each provider.
        Returns:
            dict[str, list[Article]]: A dictionary mapping providers names to their list of Articles
        Raises:
            Exception: If all wrappers fail to provide results.
        """
        return self.handler.try_call_all(lambda w: w.get_latest_news(query, limit))
