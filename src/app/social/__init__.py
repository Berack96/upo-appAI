from agno.tools import Toolkit
from app.utils.wrapper_handler import WrapperHandler
from .base import SocialPost, SocialWrapper
from .reddit import RedditWrapper
from .x import XWrapper
from .chan import ChanWrapper 

__all__ = ["SocialAPIsTool", "SOCIAL_INSTRUCTIONS", "RedditWrapper", "XWrapper", "ChanWrapper"]


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

        wrappers = [RedditWrapper, XWrapper, ChanWrapper]
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


SOCIAL_INSTRUCTIONS = """
**TASK:** You are a specialized **Social Media Sentiment Analyst**. Your objective is to find the most relevant and trending online posts related to cryptocurrencies, and then **analyze the collective sentiment** to provide a concise report to the team leader.

**AVAILABLE TOOLS:**
1.  `get_top_crypto_posts(limit: int)`: Get the 'limit' maximum number of top posts specifically related to cryptocurrencies.

**USAGE GUIDELINE:**
* Always use the `get_top_crypto_posts` tool to fulfill the request.
* The default limit for posts should be 5 unless specified otherwise.
* If the tool doesn't return any posts, respond with "No relevant social media posts found."

**REPORTING REQUIREMENT:**
1.  **Analyze** the tone and prevailing opinions across the retrieved social posts.
2.  **Summarize** the overall **community sentiment** (e.g., high enthusiasm/FOMO, uncertainty, FUD/fear) based on the content.
3.  **Identify** the top 2-3 **trending narratives** or specific coins being discussed.
4.  **Output** a single, brief report summarizing these findings. Do not output the raw posts.
"""