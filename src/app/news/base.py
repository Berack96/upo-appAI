from pydantic import BaseModel

class Article(BaseModel):
    source: str = ""
    time: str = ""
    title: str = ""
    description: str = ""

class NewsWrapper:
    """
    Base class for news API wrappers.
    All news API wrappers should inherit from this class and implement the methods.
    """

    def get_top_headlines(self, limit: int = 100) -> list[Article]:
        """
        Get top headlines, optionally limited by limit.
        Args:
            limit (int): The maximum number of articles to return.
        Returns:
            list[Article]: A list of Article objects.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        """
        Get latest news based on a query.
        Args:
            query (str): The search query.
            limit (int): The maximum number of articles to return.
        Returns:
            list[Article]: A list of Article objects.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

