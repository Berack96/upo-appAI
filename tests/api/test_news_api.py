import pytest
from app.news import NewsApiWrapper


@pytest.mark.news
@pytest.mark.api
class TestNewsAPI:

    def test_news_api_initialization(self):
        news_api = NewsApiWrapper()
        assert news_api.client is not None

    def test_news_api_get_latest_news(self):
        news_api = NewsApiWrapper()
        articles = news_api.get_latest_news(query="crypto", total=2)
        assert isinstance(articles, list)
        assert len(articles) > 0 # Ensure we got some articles (apparently it doesn't always return the requested number)
        for article in articles:
            assert hasattr(article, 'source')
            assert hasattr(article, 'time')
            assert hasattr(article, 'title')
            assert hasattr(article, 'description')


    def test_news_api_get_top_headlines(self):
        news_api = NewsApiWrapper()
        articles = news_api.get_top_headlines(query="crypto", total=2)
        assert isinstance(articles, list)
        assert len(articles) > 0 # Ensure we got some articles (apparently it doesn't always return the requested number)
        for article in articles:
            assert hasattr(article, 'source')
            assert hasattr(article, 'time')
            assert hasattr(article, 'title')
            assert hasattr(article, 'description')

