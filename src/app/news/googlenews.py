from gnews import GNews
from app.news.base import Article, NewsWrapper


def extract_article(result: dict) -> Article:
    article = Article()
    article.source = result.get("source", "")
    article.time = result.get("publishedAt", "")
    article.title = result.get("title", "")
    article.description = result.get("description", "")
    return article

class GoogleNewsWrapper(NewsWrapper):
    """
    A wrapper for the Google News RSS Feed (Documentation: https://github.com/ranahaani/GNews/?tab=readme-ov-file#about-gnews)
    It does not require an API key and is free to use.
    """

    def get_top_headlines(self, limit: int = 100) -> list[Article]:
        gnews = GNews(language='en', max_results=limit, period='7d')
        results = gnews.get_top_news()

        articles = []
        for result in results:
            article = extract_article(result)
            articles.append(article)
        return articles

    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        gnews = GNews(language='en', max_results=limit, period='7d')
        results = gnews.get_news(query)

        articles = []
        for result in results:
            article = extract_article(result)
            articles.append(article)
        return articles
