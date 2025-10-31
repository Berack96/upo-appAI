from agno.tools import Toolkit

from app.agents.action_registry import friendly_action
from app.api.wrapper_handler import WrapperHandler
from app.api.core.social import SocialPost, SocialWrapper
from app.api.social import *
from app.configs import AppConfig


class SocialAPIsTool(SocialWrapper, Toolkit):
    """
    Aggregates multiple social media API wrappers and manages them using WrapperHandler.
    This class supports retrieving top crypto-related posts by querying multiple sources.
    Providers can be configured in configs.yaml under api.social_providers.

    By default, it returns results from the first successful wrapper. 
    Optionally, it can be configured to collect posts from all wrappers.
    If no wrapper succeeds, an exception is raised.
    """

    def __init__(self):
        """
        Initialize the SocialAPIsTool with social media API wrappers configured in configs.yaml.
        The order of wrappers is determined by the api.social_providers list in the configuration.
        """
        config = AppConfig()

        self.handler = WrapperHandler.build_wrappers(
            constructors=[RedditWrapper, XWrapper, ChanWrapper],
            filters=config.api.social_providers,
            try_per_wrapper=config.api.retry_attempts,
            retry_delay=config.api.retry_delay_seconds
        )

        Toolkit.__init__( # type: ignore
            self,
            name="Socials Toolkit",
            tools=[
                self.get_top_crypto_posts,
                self.get_top_crypto_posts_aggregated,
            ],
        )

    @friendly_action("📱 Cerco i post più popolari sui social...")
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

    @friendly_action("🌐 Raccolgo i post da tutte le piattaforme social...")
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
