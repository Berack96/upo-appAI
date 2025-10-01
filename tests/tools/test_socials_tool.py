import pytest
from app.social import SocialAPIsTool


@pytest.mark.tools
@pytest.mark.social
@pytest.mark.api
class TestSocialAPIsTool:
    def test_social_api_tool(self):
        tool = SocialAPIsTool()
        assert tool is not None

    def test_social_api_tool_get_top(self):
        tool = SocialAPIsTool()
        result = tool.wrapper_handler.try_call(lambda w: w.get_top_crypto_posts(limit=2))
        assert isinstance(result, list)
        assert len(result) > 0
        for post in result:
            assert post.title is not None
            assert post.time is not None

    def test_social_api_tool_get_top__all_results(self):
        tool = SocialAPIsTool()
        result = tool.wrapper_handler.try_call_all(lambda w: w.get_top_crypto_posts(limit=2))
        assert isinstance(result, dict)
        assert len(result.keys()) > 0
        print("Results from providers:", result.keys())
        for provider, posts in result.items():
            for post in posts:
                print(provider, post.title)
                assert post.title is not None
                assert post.time is not None
