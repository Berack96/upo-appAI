import pytest
from app.news import NewsAPIsTool


@pytest.mark.tools
@pytest.mark.news
@pytest.mark.api
class TestNewsAPITool:
    def test_news_api_tool(self):
        tool = NewsAPIsTool()
        assert tool is not None

    def test_news_api_tool_get_top(self):
        tool = NewsAPIsTool()
        result = tool.wrapper_handler.try_call(lambda w: w.get_top_headlines(limit=2))
        assert isinstance(result, list)
        assert len(result) > 0
        for article in result:
            assert article.title is not None
            assert article.source is not None

    def test_news_api_tool_get_latest(self):
        tool = NewsAPIsTool()
        result = tool.wrapper_handler.try_call(lambda w: w.get_latest_news(query="crypto", limit=2))
        assert isinstance(result, list)
        assert len(result) > 0
        for article in result:
            assert article.title is not None
            assert article.source is not None

    def test_news_api_tool_get_top__all_results(self):
        tool = NewsAPIsTool()
        result = tool.wrapper_handler.try_call_all(lambda w: w.get_top_headlines(limit=2))
        assert isinstance(result, dict)
        assert len(result.keys()) > 0
        for provider, articles in result.items():
            for article in articles:
                assert article.title is not None
                assert article.source is not None

    def test_news_api_tool_get_latest__all_results(self):
        tool = NewsAPIsTool()
        result = tool.wrapper_handler.try_call_all(lambda w: w.get_latest_news(query="crypto", limit=2))
        assert isinstance(result, dict)
        assert len(result.keys()) > 0
        for provider, articles in result.items():
            for article in articles:
                assert article.title is not None
                assert article.source is not None
