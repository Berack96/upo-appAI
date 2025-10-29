from typing import Any
from ddgs import DDGS
from app.api.core.news import Article, NewsWrapper


def extract_article(result: dict[str, Any]) -> Article:
    article = Article()
    article.source = result.get("source", "")
    article.time = result.get("date", "")
    article.title = result.get("title", "")
    article.description = result.get("body", "")
    article.url = result.get("url", "")
    return article

class DuckDuckGoWrapper(NewsWrapper):
    """
    A wrapper for DuckDuckGo News search using the Tool from agno.tools.duckduckgo.
    It can be rewritten to use direct API calls if needed in the future, but currently is easy to write and use.
    """

    def __init__(self):
        self.tool = DDGS()
        self.query = "crypto"

    def get_top_headlines(self, limit: int = 100) -> list[Article]:
        results = self.tool.news(self.query, max_results=limit)
        return [extract_article(result) for result in results]

    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        results = self.tool.news(query or self.query, max_results=limit)
        return [extract_article(result) for result in results]

