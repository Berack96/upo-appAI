import os
from typing import Any
import newsapi # type: ignore
from app.api.core.news import Article, NewsWrapper


def extract_article(result: dict[str, Any]) -> Article:
    article = Article()
    article.source = result.get("source", {}).get("name", "")
    article.time = result.get("publishedAt", "")
    article.title = result.get("title", "")
    article.description = result.get("description", "")
    article.url = result.get("url", "")
    return article

class NewsApiWrapper(NewsWrapper):
    """
    A wrapper for the NewsAPI (Documentation: https://newsapi.org/docs/get-started)
    Requires an API key set in the environment variable NEWS_API_KEY.
    It is free to use, but has rate limits and restrictions based on the plan type (the free plan is 'developer' with 100 req/day).
    """

    def __init__(self):
        api_key = os.getenv("NEWS_API_KEY")
        assert api_key, "NEWS_API_KEY environment variable not set"

        self.client = newsapi.NewsApiClient(api_key=api_key)
        self.category = "business" # Cryptocurrency is under business
        self.language = "en"
        self.max_page_size = 100

    def __calc_pages(self, limit: int, page_size: int) -> tuple[int, int]:
        page_size = min(self.max_page_size, limit)
        pages = (limit // page_size) + (1 if limit % page_size > 0 else 0)
        return pages, page_size

    def get_top_headlines(self, limit: int = 100) -> list[Article]:
        pages, page_size = self.__calc_pages(limit, self.max_page_size)
        articles: list[Article] = []

        for page in range(1, pages + 1):
            headlines: dict[str, Any] = self.client.get_top_headlines(q="", category=self.category, language=self.language, page_size=page_size, page=page) # type: ignore
            results = [extract_article(article) for article in headlines.get("articles", [])] # type: ignore
            articles.extend(results)
        return articles

    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        pages, page_size = self.__calc_pages(limit, self.max_page_size)
        articles: list[Article] = []

        for page in range(1, pages + 1):
            everything: dict[str, Any] = self.client.get_everything(q=query, language=self.language, sort_by="publishedAt", page_size=page_size, page=page) # type: ignore
            results = [extract_article(article) for article in everything.get("articles", [])] # type: ignore
            articles.extend(results)
        return articles
