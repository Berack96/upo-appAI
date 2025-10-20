from pydantic import BaseModel



MAX_COMMENTS = 5

class SocialPost(BaseModel):
    """
    Represents a social media post with time, title, description, and comments.
    """
    time: str = ""
    title: str = ""
    description: str = ""
    comments: list["SocialComment"] = []

class SocialComment(BaseModel):
    """
    Represents a comment on a social media post.
    """
    time: str = ""
    description: str = ""


class SocialWrapper:
    """
    Base class for social media API wrappers.
    All social media API wrappers should inherit from this class and implement the methods.
    Provides interface for retrieving social media posts and comments from APIs.
    """

    def get_top_crypto_posts(self, limit: int = 5) -> list[SocialPost]:
        """
        Retrieve top cryptocurrency-related posts, optionally limited by the specified number.
        Args:
            limit (int): The maximum number of posts to return.
        Returns:
            list[SocialPost]: A list of SocialPost objects.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

