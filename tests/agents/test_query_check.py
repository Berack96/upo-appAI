import pytest
from app.agents.core import QueryOutputs
from app.agents.prompts import QUERY_CHECK_INSTRUCTIONS
from app.configs import AppConfig


class TestQueryCheckAgent:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.configs = AppConfig.load()
        self.model = self.configs.get_model_by_name("qwen3:1.7b")
        self.agent = self.model.get_agent(QUERY_CHECK_INSTRUCTIONS, output_schema=QueryOutputs)

    def test_query_not_ok(self):
        response = self.agent.run("Is the sky blue?")  #type: ignore
        assert response is not None
        assert response.content is not None
        content = response.content
        assert isinstance(content, QueryOutputs)
        assert content.is_crypto == False

    def test_query_not_ok2(self):
        response = self.agent.run("What is the capital of France?")  #type: ignore
        assert response is not None
        assert response.content is not None
        content = response.content
        assert isinstance(content, QueryOutputs)
        assert content.is_crypto == False

    def test_query_ok(self):
        response = self.agent.run("Bitcoin")  #type: ignore
        assert response is not None
        assert response.content is not None
        content = response.content
        assert isinstance(content, QueryOutputs)
        assert content.is_crypto == True

    def test_query_ok2(self):
        response = self.agent.run("Ha senso investire in Ethereum?")  #type: ignore
        assert response is not None
        assert response.content is not None
        content = response.content
        assert isinstance(content, QueryOutputs)
        assert content.is_crypto == True




