import pytest
from app.news import GnewsWrapper


@pytest.mark.news
@pytest.mark.api
class TestGnewsAPI:

    def test_gnews_api_initialization(self):
        gnews_api = GnewsWrapper()
        assert gnews_api is not None

    def test_gnews_api_get_latest_news(self):
        gnews_api = GnewsWrapper()
        articles = gnews_api.get_latest_news(query="crypto", total=2)
        assert isinstance(articles, list)
        assert len(articles) == 2
        for article in articles:
            assert hasattr(article, 'source')
            assert hasattr(article, 'time')
            assert hasattr(article, 'title')
            assert hasattr(article, 'description')

    def test_gnews_api_get_top_headlines(self):
        news_api = GnewsWrapper()
        articles = news_api.get_top_headlines(query="crypto", total=2)
        assert isinstance(articles, list)
        assert len(articles) == 2
        for article in articles:
            assert hasattr(article, 'source')
            assert hasattr(article, 'time')
            assert hasattr(article, 'title')
            assert hasattr(article, 'description')

