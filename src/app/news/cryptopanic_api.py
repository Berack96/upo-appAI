import os
import requests
from enum import Enum
from app.news.base import NewsWrapper, Article


class CryptoPanicFilter(Enum):
    RISING = "rising"
    HOT = "hot"
    BULLISH = "bullish"
    BEARISH = "bearish"
    IMPORTANT = "important"
    SAVED = "saved"
    LOL = "lol"
    ANY = ""

class CryptoPanicKind(Enum):
    NEWS = "news"
    MEDIA = "media"
    ALL = "all"

def extract_articles(response: dict) -> list[Article]:
    articles = []
    if 'results' in response:
        for item in response['results']:
            article = Article()
            article.source = item.get('source', {}).get('title', '')
            article.time = item.get('published_at', '')
            article.title = item.get('title', '')
            article.description = item.get('description', '')
            articles.append(article)
    return articles

class CryptoPanicWrapper(NewsWrapper):
    """
    A wrapper for the CryptoPanic API (Documentation: https://cryptopanic.com/developers/api/)
    Requires an API key set in the environment variable CRYPTOPANIC_API_KEY.
    It is free to use, but has rate limits and restrictions based on the plan type (the free plan is 'developer' with 100 req/month).
    Supports different plan types via the CRYPTOPANIC_API_PLAN environment variable (developer, growth, enterprise).
    """

    def __init__(self):
        self.api_key = os.getenv("CRYPTOPANIC_API_KEY", "")
        assert self.api_key, "CRYPTOPANIC_API_KEY environment variable not set"

        # Set here for the future, but currently not needed
        plan_type = os.getenv("CRYPTOPANIC_API_PLAN", "developer").lower()
        assert plan_type in ["developer", "growth", "enterprise"], "Invalid CRYPTOPANIC_API_PLAN value"

        self.base_url = f"https://cryptopanic.com/api/{plan_type}/v2"
        self.filter = CryptoPanicFilter.ANY
        self.kind = CryptoPanicKind.NEWS

    def get_base_params(self) -> dict[str, str]:
        params = {}
        params['public'] = 'true' # recommended for app and bots
        params['auth_token'] = self.api_key
        params['kind'] = self.kind.value
        if self.filter != CryptoPanicFilter.ANY:
            params['filter'] = self.filter.value
        return params

    def set_filter(self, filter: CryptoPanicFilter):
        self.filter = filter

    def get_top_headlines(self, limit: int = 100) -> list[Article]:
        return self.get_latest_news("", limit) # same endpoint so just call the other method

    def get_latest_news(self, query: str, limit: int = 100) -> list[Article]:
        params = self.get_base_params()
        params['currencies'] = query

        response = requests.get(f"{self.base_url}/posts/", params=params)
        assert response.status_code == 200, f"Error fetching data: {response}"

        json_response = response.json()
        articles = extract_articles(json_response)
        return articles[:limit]
