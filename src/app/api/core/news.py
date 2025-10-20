from pydantic import BaseModel


class Article(BaseModel):
    """
    Represents a news article with source, time, title, and description.
    """
    source: str = ""
    time: str = ""
    title: str = ""
    description: str = ""
    url: str = ""

class NewsWrapper:
    """
    Base class for news API wrappers.
    All news API wrappers should inherit from this class and implement the methods.
    Provides interface for retrieving news articles from news APIs.
    """

    def get_top_headlines(self, limit: int = 100) -> list[Article]:
        """
        Retrieve top headlines, optionally limited by the specified number.
        Args:
            limit (int): The maximum number of articles to return.
        Returns:
            list[Article]: A list of Article objects.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        """
        Retrieve the latest news based on a search query.
        Args:
            query (str): The search query.
            limit (int): The maximum number of articles to return.
        Returns:
            list[Article]: A list of Article objects.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

