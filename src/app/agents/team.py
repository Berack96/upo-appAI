from agno.team import Team
from app.api.tools import *
from app.agents.prompts import *
from app.configs import AppConfig, AppModel


def create_team_with(configs: AppConfig, model: AppModel, coordinator: AppModel | None = None) -> Team:

    market_tool = MarketAPIsTool(currency=configs.api.currency)
    market_tool.handler.set_retries(configs.api.retry_attempts, configs.api.retry_delay_seconds)
    news_tool = NewsAPIsTool()
    news_tool.handler.set_retries(configs.api.retry_attempts, configs.api.retry_delay_seconds)
    social_tool = SocialAPIsTool()
    social_tool.handler.set_retries(configs.api.retry_attempts, configs.api.retry_delay_seconds)

    market_agent = model.get_agent(instructions=MARKET_INSTRUCTIONS, name="MarketAgent", tools=[market_tool])
    news_agent = model.get_agent(instructions=NEWS_INSTRUCTIONS, name="NewsAgent", tools=[news_tool])
    social_agent = model.get_agent(instructions=SOCIAL_INSTRUCTIONS, name="SocialAgent", tools=[social_tool])

    coordinator = coordinator or model
    return Team(
        model=coordinator.get_model(COORDINATOR_INSTRUCTIONS),
        name="CryptoAnalysisTeam",
        members=[market_agent, news_agent, social_agent],
    )
