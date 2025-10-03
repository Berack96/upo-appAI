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
            ],
        )

    # TODO Pensare se ha senso restituire i post da TUTTI i wrapper o solo dal primo che funziona
    # la modifica è banale, basta usare try_call_all invece di try_call
    def get_top_crypto_posts(self, limit: int = 5) -> list[SocialPost]:
        return self.wrapper_handler.try_call(lambda w: w.get_top_crypto_posts(limit))
