from agno.team import Team
from app.api.markets import MarketAPIsTool
from app.api.news import NewsAPIsTool
from app.api.social import SocialAPIsTool
from app.agents.prompts import *
from app.configs import AppModel


def create_team_with(model: AppModel, coordinator: AppModel | None = None) -> Team:
    market_agent = model.get_agent(
        instructions=MARKET_INSTRUCTIONS,
        name="MarketAgent",
        tools=[MarketAPIsTool()]
    )
    news_agent = model.get_agent(
        instructions=NEWS_INSTRUCTIONS,
        name="NewsAgent",
        tools=[NewsAPIsTool()]
    )
    social_agent = model.get_agent(
        instructions=SOCIAL_INSTRUCTIONS,
        name="SocialAgent",
        tools=[SocialAPIsTool()]
    )

    coordinator = coordinator or model
    return Team(
        model=coordinator.get_model(COORDINATOR_INSTRUCTIONS),
        name="CryptoAnalysisTeam",
        members=[market_agent, news_agent, social_agent],
    )
