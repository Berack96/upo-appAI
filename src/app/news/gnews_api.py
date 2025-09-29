from gnews import GNews
from .base import Article, NewsWrapper

def result_to_article(result: dict) -> Article:
    article = Article()
    article.source = result.get("source", "")
    article.time = result.get("publishedAt", "")
    article.title = result.get("title", "")
    article.description = result.get("description", "")
    return article

class GnewsWrapper(NewsWrapper):
    def get_top_headlines(self, query: str, total: int = 100) -> list[Article]:
        gnews = GNews(language='en', max_results=total, period='7d')
        results = gnews.get_top_news()

        articles = []
        for result in results:
            article = result_to_article(result)
            articles.append(article)
        return articles

    def get_latest_news(self, query: str, total: int = 100) -> list[Article]:
        gnews = GNews(language='en', max_results=total, period='7d')
        results = gnews.get_news(query)

        articles = []
        for result in results:
            article = result_to_article(result)
            articles.append(article)
        return articles
