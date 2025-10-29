from agno.tools import Toolkit
from app.api.wrapper_handler import WrapperHandler
from app.api.core.social import SocialPost, SocialWrapper
from app.api.social import *


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

        wrappers: list[type[SocialWrapper]] = [RedditWrapper, XWrapper, ChanWrapper]
        self.handler = WrapperHandler.build_wrappers(wrappers)

        Toolkit.__init__( # type: ignore
            self,
            name="Socials Toolkit",
            tools=[
                self.get_top_crypto_posts,
                self.get_top_crypto_posts_aggregated,
            ],
        )

    def get_top_crypto_posts(self, limit: int = 5) -> list[SocialPost]:
        """
        Retrieves top cryptocurrency-related posts from the *first available* social media provider.

        This method sequentially queries multiple sources (e.g., Reddit, X)
        and returns results from the first one that responds successfully.
        Use this for a fast, general overview of top social posts.

        Args:
            limit (int): The maximum number of posts to retrieve. Defaults to 5.

        Returns:
            list[SocialPost]: A list of SocialPost objects from the single successful provider.
        """
        return self.handler.try_call(lambda w: w.get_top_crypto_posts(limit))

    def get_top_crypto_posts_aggregated(self, limit_per_wrapper: int = 5) -> dict[str, list[SocialPost]]:
        """
        Retrieves top cryptocurrency-related posts from *all available providers* and aggregates the results.

        This method queries all configured social media sources and returns a dictionary
        mapping each provider's name to its list of posts.
        Use this when you need a comprehensive report or to compare sources.

        Args:
            limit_per_wrapper (int): The maximum number of posts to retrieve *from each* provider. Defaults to 5.

        Returns:
            dict[str, list[SocialPost]]: A dictionary mapping provider names (str) to their list of SocialPost objects.

        Raises:
            Exception: If all providers fail to return results.
        """
        return self.handler.try_call_all(lambda w: w.get_top_crypto_posts(limit_per_wrapper))
