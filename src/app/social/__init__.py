from .base import SocialPost, SocialWrapper
from .reddit import RedditWrapper
from app.utils.wrapper_handler import WrapperHandler
from agno.tools import Toolkit

__all__ = ["SocialAPIsTool", "SOCIAL_INSTRUCTIONS", "RedditWrapper"]

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
        self.wrapper_handler: WrapperHandler[SocialWrapper] = WrapperHandler(wrappers)

        Toolkit.__init__(
            self,
            name="Socials Toolkit",
            tools=[
                self.get_top_crypto_posts,
            ],
        )

    # TODO Pensare se ha senso restituire i post da TUTTI i wrapper o solo dal primo che funziona
    # la modifica è banale, basta usare try_call_all invece di try_call
    def get_top_crypto_posts(self, limit:int = 5) -> list[SocialPost]:
        return self.wrapper_handler.try_call(lambda w: w.get_top_crypto_posts(limit))


# TODO migliorare il prompt
SOCIAL_INSTRUCTIONS = """
Utilizza questo strumento per ottenere i post più recenti e gli argomenti di tendenza sui social media. Puoi richiedere i post più recenti o gli argomenti di tendenza.

Esempio di utilizzo:
- get_latest_news("crypto", limit=5) # ottieni le ultime 5 notizie su "crypto", la query può essere qualsiasi argomento di interesse
- get_top_headlines(limit=3) # ottieni i 3 titoli principali delle notizie globali

"""