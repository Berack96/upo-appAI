import pytest
from praw import Reddit
from app.social.reddit import MAX_COMMENTS, RedditWrapper

@pytest.mark.social
@pytest.mark.api
class TestRedditWrapper:
    def test_initialization(self):
        wrapper = RedditWrapper()
        assert wrapper is not None
        assert isinstance(wrapper.tool, Reddit)

    def test_get_top_crypto_posts(self):
        wrapper = RedditWrapper()
        posts = wrapper.get_top_crypto_posts(limit=2)
        assert isinstance(posts, list)
        assert len(posts) == 2
        for post in posts:
            assert post.title != ""
            assert isinstance(post.comments, list)
            assert len(post.comments) <= MAX_COMMENTS
            for comment in post.comments:
                assert comment.description != ""
