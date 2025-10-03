from agno.tools import Toolkit
from app.utils.wrapper_handler import WrapperHandler
from app.social.base import SocialPost, SocialWrapper
from app.social.reddit import RedditWrapper

__all__ = ["SocialAPIsTool", "RedditWrapper", "SocialPost"]


class SocialAPIsTool(SocialWrapper, Toolkit):
    """
    Aggregates multiple social media API wrappers and manages them using WrapperHandler.
    This class supports retrieving top crypto-related posts by querying multiple sources:
    - RedditWrapper

    By default, it returns results from the first successful wrapper. 
    Optionally, it can be configured to collect posts from all wrappers.
    If no wrapper succeeds, an exception is raised.
    """

    def __init__(self):
        """
        Initialize the SocialAPIsTool with multiple social media API wrappers.
        The tool uses WrapperHandler to manage and invoke the different social media API wrappers.
        The following wrappers are included in this order:
        - RedditWrapper.
        """

        wrappers = [RedditWrapper]
        self.wrapper_handler: WrapperHandler[SocialWrapper] = WrapperHandler.build_wrappers(wrappers)

        Toolkit.__init__(
            self,
            name="Socials Toolkit",
            tools=[
                self.get_top_crypto_posts,
                self.get_top_crypto_posts_aggregated,
            ],
        )

    def get_top_crypto_posts(self, limit: int = 5) -> list[SocialPost]:
        return self.wrapper_handler.try_call(lambda w: w.get_top_crypto_posts(limit))

    def get_top_crypto_posts_aggregated(self, limit_per_wrapper: int = 5) -> dict[str, list[SocialPost]]:
        """
        Calls get_top_crypto_posts on all wrappers/providers and returns a dictionary mapping their names to their posts.
        Args:
            limit_per_wrapper (int): Maximum number of posts to retrieve from each provider.
        Returns:
            dict[str, list[SocialPost]]: A dictionary where keys are wrapper names and values are lists of SocialPost objects.
        Raises:
            Exception: If all wrappers fail to provide results.
        """
        return self.wrapper_handler.try_call_all(lambda w: w.get_top_crypto_posts(limit_per_wrapper))
