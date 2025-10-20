import re
import pytest
from app.api.social.chan import ChanWrapper

@pytest.mark.social
@pytest.mark.api
class TestChanWrapper:
    def test_initialization(self):
        wrapper = ChanWrapper()
        assert wrapper is not None

    def test_get_top_crypto_posts(self):
        wrapper = ChanWrapper()
        posts = wrapper.get_top_crypto_posts(limit=2)
        assert isinstance(posts, list)
        assert len(posts) == 2
        for post in posts:
            assert post.title != ""
            assert post.time != ""
            assert re.match(r'\d{4}-\d{2}-\d{2}', post.time)
            assert isinstance(post.comments, list)

