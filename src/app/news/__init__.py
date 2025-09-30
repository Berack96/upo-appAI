from app.utils.wrapper_handler import WrapperHandler
from .base import NewsWrapper, Article
from .news_api import NewsApiWrapper
from .gnews_api import GoogleNewsWrapper
from .cryptopanic_api import CryptoPanicWrapper
from .duckduckgo import DuckDuckGoWrapper

__all__ = ["NewsApiWrapper", "GoogleNewsWrapper", "CryptoPanicWrapper", "DuckDuckGoWrapper"]


class NewsAPIs(NewsWrapper):
    """
    A wrapper class that aggregates multiple news API wrappers and tries them in order until one succeeds.
    This class uses the WrapperHandler to manage multiple NewsWrapper instances.
    It includes, and tries, the following news API wrappers in this order:
    - GnewsWrapper
    - DuckDuckGoWrapper
    - NewsApiWrapper
    - CryptoPanicWrapper

    It provides methods to get top headlines and latest news by delegating the calls to the first successful wrapper.
    If all wrappers fail, it raises an exception.
    """

    def __init__(self):
        wrappers = [GoogleNewsWrapper, DuckDuckGoWrapper, NewsApiWrapper, CryptoPanicWrapper]
        self.wrapper_handler: WrapperHandler[NewsWrapper] = WrapperHandler.build_wrappers(wrappers)

    def get_top_headlines(self, total: int = 100) -> list[Article]:
        return self.wrapper_handler.try_call(lambda w: w.get_top_headlines(total))
    def get_latest_news(self, query: str, total: int = 100) -> list[Article]:
        return self.wrapper_handler.try_call(lambda w: w.get_latest_news(query, total))
