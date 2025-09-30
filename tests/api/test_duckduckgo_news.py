import pytest
from app.news import DuckDuckGoWrapper


@pytest.mark.news
@pytest.mark.api
class TestDuckDuckGoNews:

    def test_news_api_initialization(self):
        news = DuckDuckGoWrapper()
        assert news.tool is not None

    def test_news_api_get_latest_news(self):
        news = DuckDuckGoWrapper()
        articles = news.get_latest_news(query="crypto", total=2)
        assert isinstance(articles, list)
        assert len(articles) == 2
        for article in articles:
            assert article.source is not None or article.source != ""
            assert article.time is not None or article.time != ""
            assert article.title is not None or article.title != ""
            assert article.description is not None or article.description != ""


    def test_news_api_get_top_headlines(self):
        news = DuckDuckGoWrapper()
        articles = news.get_top_headlines(total=2)
        assert isinstance(articles, list)
        assert len(articles) == 2
        for article in articles:
            assert article.source is not None or article.source != ""
            assert article.time is not None or article.time != ""
            assert article.title is not None or article.title != ""
            assert article.description is not None or article.description != ""

