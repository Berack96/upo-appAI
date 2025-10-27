import pytest
from app.agents.prompts import REPORT_GENERATION_INSTRUCTIONS
from app.configs import AppConfig


class TestReportGenerationAgent:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.configs = AppConfig.load()
        self.model = self.configs.get_model_by_name("qwen3:1.7b")
        self.agent = self.model.get_agent(REPORT_GENERATION_INSTRUCTIONS)

    def test_report_generation(self):
        sample_data = """
        The analysis reported from the Market Agent have highlighted the following key metrics for the cryptocurrency market:
        Bitcoin (BTC) has shown strong performance over the last 24 hours with a price of $30,000 and a Market Cap of $600 Billion
        Ethereum (ETH) is currently priced at $2,000 with a Market Cap of $250 Billion and a 24h Volume of $20 Billion.
        The overall market sentiment is bullish with a 5% increase in total market capitalization.
        No significant regulatory news has been reported and the social media sentiment remains unknown.
        """

        response = self.agent.run(sample_data)  # type: ignore
        assert response is not None
        assert response.content is not None
        content = response.content
        assert isinstance(content, str)
        print(content)
        assert "Bitcoin" in content
        assert "Ethereum" in content
        assert "Summary" in content

