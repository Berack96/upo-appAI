import asyncio
import logging
from typing import Callable, Self
from agno.run.agent import RunOutputEvent
from agno.team import Team, TeamRunEvent, TeamRunOutputEvent
from agno.tools.reasoning import ReasoningTools
from app.agents import AppModels
from app.markets import MarketAPIsTool
from app.news import NewsAPIsTool
from app.social import SocialAPIsTool

logging = logging.getLogger("AppTeam")


class AllTools:
    __instance: Self

    def __new__(cls) -> Self:
        if not hasattr(cls, "__instance"):
            cls.__instance = super(AllTools, cls).__new__(cls)
        return cls.__instance

    # TODO scegliere un modo migliore per inizializzare gli strumenti
    # TODO magari usare un config file o una classe apposta per i configs
    def __init__(self):
        self.market = MarketAPIsTool("EUR")
        self.news = NewsAPIsTool()
        self.social = SocialAPIsTool()


class AppTeam:
    def __init__(self, team_models: AppModels, coordinator: AppModels | None = None):
        self.team_models = team_models
        self.coordinator = coordinator or team_models
        self.listeners: dict[str, Callable[[RunOutputEvent | TeamRunOutputEvent], None]] = {}

    def add_listener(self, event: str, listener: Callable[[RunOutputEvent | TeamRunOutputEvent], None]) -> None:
        self.listeners[event] = listener

    def run_team(self, query: str) -> str:
        return asyncio.run(self.run_team_async(query))

    async def run_team_async(self, query: str) -> str:
        logging.info(f"Running team q='{query}'")
        team = AppTeam.create_team_with(self.team_models, self.coordinator)
        result = "No output from team"

        async for run_event in team.arun(query, stream=True, stream_intermediate_steps=True): # type: ignore
            if run_event.event in self.listeners:
                self.listeners[run_event.event](run_event)
            if run_event.event in [TeamRunEvent.run_completed]:
                if isinstance(run_event.content, str):
                    result = run_event.content
                    thinking = result.rfind("</think>")
                    if thinking != -1: result = result[thinking:]

        logging.info(f"Team finished")
        return result

    @staticmethod
    def create_team_with(models: AppModels, coordinator: AppModels) -> Team:
        tools = AllTools()

        market_agent = models.get_agent(
            instructions=MARKET_INSTRUCTIONS,
            name="MarketAgent",
            tools=[tools.market]
        )
        news_agent = models.get_agent(
            instructions=NEWS_INSTRUCTIONS,
            name="NewsAgent",
            tools=[tools.news]
        )
        social_agent = models.get_agent(
            instructions=SOCIAL_INSTRUCTIONS,
            name="SocialAgent",
            tools=[tools.social]
        )

        return Team(
            model=coordinator.get_model(COORDINATOR_INSTRUCTIONS),
            name="CryptoAnalysisTeam",
            members=[market_agent, news_agent, social_agent],
            tools=[ReasoningTools()]
        )

COORDINATOR_INSTRUCTIONS = """
You are the expert coordinator of a financial analysis team specializing in cryptocurrencies.

Your team consists of three agents:
- **MarketAgent**: Provides quantitative market data, price analysis, and technical indicators.
- **NewsAgent**: Scans and analyzes the latest news, articles, and official announcements.
- **SocialAgent**: Gauges public sentiment, trends, and discussions on social media.

Your primary objective is to answer the user's query by orchestrating the work of your team members.

Your workflow is as follows:
1.  **Deconstruct the user's query** to identify the required information.
2.  **Delegate specific tasks** to the most appropriate agent(s) to gather the necessary data and initial analysis.
3.  **Analyze the information** returned by the agents.
4.  If the initial data is insufficient or the query is complex, **iteratively re-engage the agents** with follow-up questions to build a comprehensive picture.
5.  **Synthesize all the gathered information** into a final, coherent, and complete analysis that fills all the required output fields.
"""

MARKET_INSTRUCTIONS = """
**TASK:** You are a specialized **Crypto Price Data Retrieval Agent**. Your primary goal is to fetch the most recent and/or historical price data for requested cryptocurrency assets (e.g., 'BTC', 'ETH', 'SOL'). You must provide the data in a clear and structured format.

**AVAILABLE TOOLS:**
1.  `get_products(asset_ids: list[str])`: Get **current** product/price info for a list of assets. **(PREFERITA: usa questa per i prezzi live)**
2.  `get_historical_prices(asset_id: str, limit: int)`: Get historical price data for one asset. Default limit is 100. **(PREFERITA: usa questa per i dati storici)**
3.  `get_products_aggregated(asset_ids: list[str])`: Get **aggregated current** product/price info for a list of assets. **(USA SOLO SE richiesto 'aggregato' o se `get_products` fallisce)**
4.  `get_historical_prices_aggregated(asset_id: str, limit: int)`: Get **aggregated historical** price data for one asset. **(USA SOLO SE richiesto 'aggregato' o se `get_historical_prices` fallisce)**

**USAGE GUIDELINE:**
* **Asset ID:** Always convert common names (e.g., 'Bitcoin', 'Ethereum') into their official ticker/ID (e.g., 'BTC', 'ETH').
* **Cost Management (Cruciale per LLM locale):** Prefer `get_products` and `get_historical_prices` for standard requests to minimize costs.
* **Aggregated Data:** Use `get_products_aggregated` or `get_historical_prices_aggregated` only if the user specifically requests aggregated data or you value that having aggregated data is crucial for the analysis.
* **Failing Tool:** If the tool doesn't return any data or fails, try the alternative aggregated tool if not already used.

**REPORTING REQUIREMENT:**
1.  **Format:** Output the results in a clear, easy-to-read list or table.
2.  **Live Price Request:** If an asset's *current price* is requested, report the **Asset ID**, **Latest Price**, and **Time/Date of the price**.
3.  **Historical Price Request:** If *historical data* is requested, report the **Asset ID**, the **Limit** of points returned, and the **First** and **Last** entries from the list of historical prices (Date, Price).
4.  **Output:** For all requests, output a single, concise summary of the findings; if requested, also include the raw data retrieved.
"""

NEWS_INSTRUCTIONS = """
**TASK:** You are a specialized **Crypto News Analyst**. Your goal is to fetch the latest news or top headlines related to cryptocurrencies, and then **analyze the sentiment** of the content to provide a concise report to the team leader. Prioritize 'crypto' or specific cryptocurrency names (e.g., 'Bitcoin', 'Ethereum') in your searches.

**AVAILABLE TOOLS:**
1.  `get_latest_news(query: str, limit: int)`: Get the 'limit' most recent news articles for a specific 'query'.
2.  `get_top_headlines(limit: int)`: Get the 'limit' top global news headlines.
3.  `get_latest_news_aggregated(query: str, limit: int)`: Get aggregated latest news articles for a specific 'query'.
4.  `get_top_headlines_aggregated(limit: int)`: Get aggregated top global news headlines.

**USAGE GUIDELINE:**
* Always use `get_latest_news` with a relevant crypto-related query first.
* The default limit for news items should be 5 unless specified otherwise.
* If the tool doesn't return any articles, respond with "No relevant news articles found."

**REPORTING REQUIREMENT:**
1.  **Analyze** the tone and key themes of the retrieved articles.
2.  **Summarize** the overall **market sentiment** (e.g., highly positive, cautiously neutral, generally negative) based on the content.
3.  **Identify** the top 2-3 **main topics** discussed (e.g., new regulation, price surge, institutional adoption).
4.  **Output** a single, brief report summarizing these findings. Do not output the raw articles.
"""

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
