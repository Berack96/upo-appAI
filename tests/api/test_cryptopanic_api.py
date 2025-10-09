import os
import pytest
from app.api.news import CryptoPanicWrapper


@pytest.mark.limited
@pytest.mark.news
@pytest.mark.api
@pytest.mark.skipif(not os.getenv("CRYPTOPANIC_API_KEY"), reason="CRYPTOPANIC_API_KEY not set")
class TestCryptoPanicAPI:

    def test_crypto_panic_api_initialization(self):
        crypto = CryptoPanicWrapper()
        assert crypto is not None

    def test_crypto_panic_api_get_latest_news(self):
        crypto = CryptoPanicWrapper()
        articles = crypto.get_latest_news(query="", limit=2)
        assert isinstance(articles, list)
        assert len(articles) == 2
        for article in articles:
            assert article.source is not None or article.source != ""
            assert article.time is not None or article.time != ""
            assert article.title is not None or article.title != ""
            assert article.description is not None or article.description != ""

    # Useless since both methods use the same endpoint
    # def test_crypto_panic_api_get_top_headlines(self):
    #     crypto = CryptoPanicWrapper()
    #     articles = crypto.get_top_headlines(total=2)
    #     assert isinstance(articles, list)
    #     assert len(articles) == 2
    #     for article in articles:
    #         assert article.source is not None or article.source != ""
    #         assert article.time is not None or article.time != ""
    #         assert article.title is not None or article.title != ""
    #         assert article.description is not None or article.description != ""

