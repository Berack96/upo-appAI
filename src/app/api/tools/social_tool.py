from agno.tools import Toolkit
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

    # Mapping of wrapper names to wrapper classes
    _WRAPPER_MAP = {
        'RedditWrapper': RedditWrapper,
        'XWrapper': XWrapper,
        'ChanWrapper': ChanWrapper,
    }

    def __init__(self):
        """
        Initialize the SocialAPIsTool with social media API wrappers configured in configs.yaml.
        The order of wrappers is determined by the api.social_providers list in the configuration.
        """
        config = AppConfig()
        
        # Get wrapper classes based on configuration using the helper function
        wrappers = WrapperHandler.filter_wrappers_by_config(
            wrapper_map=self._WRAPPER_MAP,
            provider_names=config.api.social_providers,
            fallback_wrappers=[RedditWrapper, XWrapper, ChanWrapper]
        )
        
        self.handler = WrapperHandler.build_wrappers(
            wrappers,
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

    def get_top_crypto_posts(self, limit: int = 5) -> list[SocialPost]:
        return self.handler.try_call(lambda w: w.get_top_crypto_posts(limit))

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
        return self.handler.try_call_all(lambda w: w.get_top_crypto_posts(limit_per_wrapper))
