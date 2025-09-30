from app.utils.wrapper_handler import WrapperHandler
from .base import NewsWrapper, Article
from .news_api import NewsApiWrapper
from .gnews_api import GnewsWrapper
from .cryptopanic_api import CryptoPanicWrapper

__all__ = ["NewsApiWrapper", "GnewsWrapper", "CryptoPanicWrapper"]


class NewsAPIs(NewsWrapper):
    def __init__(self):
        wrappers = [GnewsWrapper, NewsApiWrapper, CryptoPanicWrapper]
        self.wrapper_handler: WrapperHandler[NewsWrapper] = WrapperHandler.build_wrappers(wrappers)

    def get_top_headlines(self, query: str, total: int = 100) -> list[Article]:
        return self.wrapper_handler.try_call(lambda w: w.get_top_headlines(query, total))
    def get_latest_news(self, query: str, total: int = 100) -> list[Article]:
        return self.wrapper_handler.try_call(lambda w: w.get_latest_news(query, total))
