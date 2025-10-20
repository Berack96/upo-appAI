import os
import re
import pytest
from app.api.social.x import XWrapper

@pytest.mark.social
@pytest.mark.api
@pytest.mark.skipif(not os.getenv("X_API_KEY"), reason="X_API_KEY not set in environment variables")
class TestXWrapper:
    def test_initialization(self):
        wrapper = XWrapper()
        assert wrapper is not None

    def test_get_top_crypto_posts(self):
        wrapper = XWrapper()
        posts = wrapper.get_top_crypto_posts(limit=2)
        assert isinstance(posts, list)
        assert len(posts) == 2
        for post in posts:
            assert post.title != ""
            assert re.match(r'\d{4}-\d{2}-\d{2}', post.time)
            assert isinstance(post.comments, list)
