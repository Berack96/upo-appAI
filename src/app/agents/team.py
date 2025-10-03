from agno.team import Team
from app.agents import AppModels
from app.markets import MARKET_INSTRUCTIONS, MarketAPIsTool
from app.news import NEWS_INSTRUCTIONS, NewsAPIsTool
from app.social import SOCIAL_INSTRUCTIONS, SocialAPIsTool


def create_team_with(models: AppModels, coordinator: AppModels | None = None) -> Team:
    market_agent = models.get_agent(
        instructions=MARKET_INSTRUCTIONS,
        name="MarketAgent",
        tools=[MarketAPIsTool()]
    )
    news_agent = models.get_agent(
        instructions=NEWS_INSTRUCTIONS,
        name="NewsAgent",
        tools=[NewsAPIsTool()]
    )
    social_agent = models.get_agent(
        instructions=SOCIAL_INSTRUCTIONS,
        name="SocialAgent",
        tools=[SocialAPIsTool()]
    )

    coordinator = coordinator or models
    return Team(
        model=coordinator.get_model(COORDINATOR_INSTRUCTIONS),
        name="CryptoAnalysisTeam",
        members=[market_agent, news_agent, social_agent],
    )

# TODO: migliorare le istruzioni del team
COORDINATOR_INSTRUCTIONS = """
Agisci come coordinatore: smista le richieste tra MarketAgent, NewsAgent e SocialAgent.
"""
