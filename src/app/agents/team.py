import asyncio
import logging
from typing import Callable
from agno.run.agent import RunOutputEvent
from agno.team import Team, TeamRunEvent, TeamRunOutputEvent
from agno.tools.reasoning import ReasoningTools
from app.agents.prompts import *
from app.configs import AppConfig, AppModel
from app.api.tools import *

logging = logging.getLogger("AppTeam")


class AppTeam:
    def __init__(self, configs: AppConfig, team_models: AppModel, coordinator: AppModel | None = None):
        self.configs = configs
        self.team_models = team_models
        self.coordinator = coordinator or team_models
        self.listeners: dict[str, Callable[[RunOutputEvent | TeamRunOutputEvent], None]] = {}

    def add_listener(self, event: str, listener: Callable[[RunOutputEvent | TeamRunOutputEvent], None]) -> None:
        self.listeners[event] = listener

    def run_team(self, query: str) -> str:
        return asyncio.run(self.run_team_async(query))

    async def run_team_async(self, query: str) -> str:
        logging.info(f"Running team q='{query}'")
        team = AppTeam.create_team_with(self.configs, self.team_models, self.coordinator)
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

    @classmethod
    def create_team_with(cls, configs: AppConfig, team_model: AppModel, team_leader: AppModel | None = None) -> Team:

        market_tool = MarketAPIsTool(currency=configs.api.currency)
        market_tool.handler.set_retries(configs.api.retry_attempts, configs.api.retry_delay_seconds)
        news_tool = NewsAPIsTool()
        news_tool.handler.set_retries(configs.api.retry_attempts, configs.api.retry_delay_seconds)
        social_tool = SocialAPIsTool()
        social_tool.handler.set_retries(configs.api.retry_attempts, configs.api.retry_delay_seconds)

        market_agent = team_model.get_agent(instructions=MARKET_INSTRUCTIONS, name="MarketAgent", tools=[market_tool])
        news_agent = team_model.get_agent(instructions=NEWS_INSTRUCTIONS, name="NewsAgent", tools=[news_tool])
        social_agent = team_model.get_agent(instructions=SOCIAL_INSTRUCTIONS, name="SocialAgent", tools=[social_tool])

        team_leader = team_leader or team_model
        return Team(
            model=team_leader.get_model(COORDINATOR_INSTRUCTIONS),
            name="CryptoAnalysisTeam",
            tools=[ReasoningTools()],
            members=[market_agent, news_agent, social_agent],
        )