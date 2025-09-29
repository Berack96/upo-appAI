from pydantic import BaseModel

class Article(BaseModel):
    source: str = ""
    time: str = ""
    title: str = ""
    description: str = ""

class NewsWrapper:
    def get_top_headlines(self, query: str, total: int = 100) -> list[Article]:
        raise NotImplementedError("This method should be overridden by subclasses")
    def get_latest_news(self, query: str, total: int = 100) -> list[Article]:
        raise NotImplementedError("This method should be overridden by subclasses")

