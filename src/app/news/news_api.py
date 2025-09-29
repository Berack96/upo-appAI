import os
import newsapi
from .base import Article


def result_to_article(result: dict) -> Article:
    article = Article()
    article.source = result.get("source", {}).get("name", "")
    article.time = result.get("publishedAt", "")
    article.title = result.get("title", "")
    article.description = result.get("description", "")
    return article

class NewsAPI:
    def __init__(self):
        api_key = os.getenv("NEWS_API_KEY")
        assert api_key is not None, "NEWS_API_KEY environment variable not set"

        self.client = newsapi.NewsApiClient(api_key=api_key)
        self.category = "business" # Cryptocurrency is under business
        self.language = "en" # TODO Only English articles for now?
        self.max_page_size = 100

    def get_top_headlines(self, query:str, total:int=100) -> list[Article]:
        page_size = min(self.max_page_size, total)
        pages = (total // page_size) + (1 if total % page_size > 0 else 0)

        articles = []
        for page in range(1, pages + 1):
            headlines = self.client.get_top_headlines(q=query, category=self.category, language=self.language, page_size=page_size, page=page)
            results = [result_to_article(article) for article in headlines.get("articles", [])]
            articles.extend(results)
        return articles


