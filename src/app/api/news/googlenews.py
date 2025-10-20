from typing import Any
from gnews import GNews # type: ignore
from app.api.core.news import Article, NewsWrapper


def extract_article(result: dict[str, Any]) -> Article:
    article = Article()
    article.source = result.get("source", "")
    article.time = result.get("publishedAt", "")
    article.title = result.get("title", "")
    article.description = result.get("description", "")
    article.url = result.get("url", "")
    return article

class GoogleNewsWrapper(NewsWrapper):
    """
    A wrapper for the Google News RSS Feed (Documentation: https://github.com/ranahaani/GNews/?tab=readme-ov-file#about-gnews)
    It does not require an API key and is free to use.
    """

    def get_top_headlines(self, limit: int = 100) -> list[Article]:
        gnews = GNews(language='en', max_results=limit, period='7d')
        results: list[dict[str, Any]] = gnews.get_top_news() # type: ignore

        articles: list[Article] = []
        for result in results:
            article = extract_article(result)
            articles.append(article)
        return articles

    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        gnews = GNews(language='en', max_results=limit, period='7d')
        results: list[dict[str, Any]] = gnews.get_news(query) # type: ignore

        articles: list[Article] = []
        for result in results:
            article = extract_article(result)
            articles.append(article)
        return articles
