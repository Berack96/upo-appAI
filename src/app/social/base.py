from pydantic import BaseModel


class SocialPost(BaseModel):
    time: str = ""
    title: str = ""
    description: str = ""
    comments: list["SocialComment"] = []

class SocialComment(BaseModel):
    time: str = ""
    description: str = ""


class SocialWrapper:
    """
    Base class for social media API wrappers.
    All social media API wrappers should inherit from this class and implement the methods.
    """
    def get_top_crypto_posts(self, limit: int = 5) -> list[SocialPost]:
        """
        Get top cryptocurrency-related posts, optionally limited by total.
        Args:
            limit (int): The maximum number of posts to return.
        Returns:
            list[SocialPost]: A list of SocialPost objects.
        """
        raise NotImplementedError("This method should be overridden by subclasses")

