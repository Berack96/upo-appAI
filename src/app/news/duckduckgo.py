import json
from agno.tools.duckduckgo import DuckDuckGoTools
from app.news.base import Article, NewsWrapper


def extract_article(result: dict) -> Article:
    article = Article()
    article.source = result.get("source", "")
    article.time = result.get("date", "")
    article.title = result.get("title", "")
    article.description = result.get("body", "")
    return article

class DuckDuckGoWrapper(NewsWrapper):
    """
    A wrapper for DuckDuckGo News search using the Tool from agno.tools.duckduckgo.
    It can be rewritten to use direct API calls if needed in the future, but currently is easy to write and use.
    """

    def __init__(self):
        self.tool = DuckDuckGoTools()
        self.query = "crypto"

    def get_top_headlines(self, limit: int = 100) -> list[Article]:
        results = self.tool.duckduckgo_news(self.query, max_results=limit)
        json_results = json.loads(results)
        return [extract_article(result) for result in json_results]

    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        results = self.tool.duckduckgo_news(query or self.query, max_results=limit)
        json_results = json.loads(results)
        return [extract_article(result) for result in json_results]

