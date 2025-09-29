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
            assert article.source is not None or article.source != ""
            assert article.time is not None or article.time != ""
            assert article.title is not None or article.title != ""
            assert article.description is not None or article.description != ""

    def test_gnews_api_get_top_headlines(self):
        news_api = GnewsWrapper()
        articles = news_api.get_top_headlines(query="crypto", total=2)
        assert isinstance(articles, list)
        assert len(articles) == 2
        for article in articles:
            assert article.source is not None or article.source != ""
            assert article.time is not None or article.time != ""
            assert article.title is not None or article.title != ""
            assert article.description is not None or article.description != ""

