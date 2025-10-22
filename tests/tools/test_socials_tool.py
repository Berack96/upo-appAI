import pytest
from app.api.tools import SocialAPIsTool


@pytest.mark.tools
@pytest.mark.social
@pytest.mark.api
class TestSocialAPIsTool:
    def test_social_api_tool(self):
        tool = SocialAPIsTool()
        assert tool is not None

    def test_social_api_tool_get_top(self):
        tool = SocialAPIsTool()
        result = tool.handler.try_call(lambda w: w.get_top_crypto_posts(limit=2))
        assert isinstance(result, list)
        assert len(result) > 0
        for post in result:
            assert post.title is not None
            assert post.timestamp is not None

    def test_social_api_tool_get_top__all_results(self):
        tool = SocialAPIsTool()
        result = tool.handler.try_call_all(lambda w: w.get_top_crypto_posts(limit=2))
        assert isinstance(result, dict)
        assert len(result.keys()) > 0
        for _provider, posts in result.items():
            for post in posts:
                assert post.title is not None
                assert post.timestamp is not None
