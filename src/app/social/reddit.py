import os
from praw import Reddit
from praw.models import Submission, MoreComments
from .base import SocialWrapper, SocialPost, SocialComment

MAX_COMMENTS = 5


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
        self.client_id = os.getenv("REDDIT_API_CLIENT_ID")
        assert self.client_id is not None, "REDDIT_API_CLIENT_ID environment variable is not set"

        self.client_secret = os.getenv("REDDIT_API_CLIENT_SECRET")
        assert self.client_secret is not None, "REDDIT_API_CLIENT_SECRET environment variable is not set"

        self.tool = Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent="upo-appAI",
        )

    def get_top_crypto_posts(self, limit:int = 5) -> list[SocialPost]:
        subreddit = self.tool.subreddit("CryptoCurrency")
        top_posts = subreddit.top(limit=limit, time_filter="week")
        return [create_social_post(post) for post in top_posts]

