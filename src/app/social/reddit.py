import os
from praw import Reddit
from praw.models import Submission, MoreComments
from .base import SocialWrapper, SocialPost, SocialComment

MAX_COMMENTS = 5
# TODO mettere piu' subreddit?
# scelti da https://lkiconsulting.io/marketing/best-crypto-subreddits/
SUBREDDITS = [
    "CryptoCurrency", 
    "Bitcoin",
    "Ethereum",
    "CryptoMarkets",
    "Dogecoin",
    "Altcoin",
    "DeFi",
    "NFT",
    "BitcoinBeginners",
    "CryptoTechnology",
    "btc" # alt subs of Bitcoin
]


def create_social_post(post: Submission) -> SocialPost:
    social = SocialPost()
    social.time = str(post.created)
    social.title = post.title
    social.description = post.selftext

    for i, top_comment in enumerate(post.comments):
        if i >= MAX_COMMENTS:
            break
        if isinstance(top_comment, MoreComments): #skip MoreComments objects
            continue

        comment = SocialComment()
        comment.time = str(top_comment.created)
        comment.description = top_comment.body
        social.comments.append(comment)
    return social

class RedditWrapper(SocialWrapper):
    """
    A wrapper for the Reddit API using PRAW (Python Reddit API Wrapper).
    Requires the following environment variables to be set:
    - REDDIT_API_CLIENT_ID
    - REDDIT_API_CLIENT_SECRET

    You can get them by creating an app at https://www.reddit.com/prefs/apps
    """

    def __init__(self):
        client_id = os.getenv("REDDIT_API_CLIENT_ID")
        assert client_id, "REDDIT_API_CLIENT_ID environment variable is not set"

        client_secret = os.getenv("REDDIT_API_CLIENT_SECRET")
        assert client_secret, "REDDIT_API_CLIENT_SECRET environment variable is not set"

        self.tool = Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="upo-appAI",
        )
        self.subreddits = self.tool.subreddit("+".join(SUBREDDITS))

    def get_top_crypto_posts(self, limit: int = 5) -> list[SocialPost]:
        top_posts = self.subreddits.top(limit=limit, time_filter="week")
        return [create_social_post(post) for post in top_posts]
