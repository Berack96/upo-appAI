import asyncio
import pytest
from app.agents.core import PipelineInputs
from app.agents.prompts import *
from app.configs import AppConfig


# fix warning about no event loop
@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.mark.slow
class TestTeamAgent:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.configs = AppConfig.load()
        self.configs.agents.team_model = "qwen3:1.7b"
        self.configs.agents.team_leader_model = "qwen3:1.7b"
        self.inputs = PipelineInputs(self.configs)
        self.team = self.inputs.get_agent_team()

    def test_team_agent_response(self):
        self.inputs.user_query = "Is Bitcoin a good investment now?"
        inputs = self.inputs.get_query_inputs()
        response = self.team.run(inputs)  # type: ignore

        assert response is not None
        assert response.content is not None
        content = response.content
        print(content)
        assert isinstance(content, str)
        assert "Bitcoin" in content
        assert False
