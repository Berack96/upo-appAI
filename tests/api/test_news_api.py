import os
import pytest
from app.news import NewsApiWrapper


@pytest.mark.news
@pytest.mark.api
@pytest.mark.skipif(not os.getenv("NEWS_API_KEY"), reason="NEWS_API_KEY not set in environment variables")
class TestNewsAPI:

    def test_news_api_initialization(self):
        news_api = NewsApiWrapper()
        assert news_api.client is not None

    def test_news_api_get_latest_news(self):
        news_api = NewsApiWrapper()
        articles = news_api.get_latest_news(query="crypto", limit=2)
        assert isinstance(articles, list)
        assert len(articles) > 0 # Ensure we got some articles (apparently it doesn't always return the requested number)
        for article in articles:
            assert article.source is not None or article.source != ""
            assert article.time is not None or article.time != ""
            assert article.title is not None or article.title != ""
            assert article.description is not None or article.description != ""


    def test_news_api_get_top_headlines(self):
        news_api = NewsApiWrapper()
        articles = news_api.get_top_headlines(limit=2)
        assert isinstance(articles, list)
        # assert len(articles) > 0 # apparently it doesn't always return SOME articles
        for article in articles:
            assert article.source is not None or article.source != ""
            assert article.time is not None or article.time != ""
            assert article.title is not None or article.title != ""
            assert article.description is not None or article.description != ""

