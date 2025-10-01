import pytest
from app.predictor import PREDICTOR_INSTRUCTIONS, PredictorInput, PredictorOutput, PredictorStyle
from app.markets.base import ProductInfo
from app.models import AppModels

def unified_checks(model: AppModels, input):
    llm = model.get_agent(PREDICTOR_INSTRUCTIONS, output=PredictorOutput) # type: ignore[arg-type]
    result = llm.run(input)
    content = result.content

    assert isinstance(content, PredictorOutput)
    assert content.strategy not in (None, "", "null")
    assert isinstance(content.strategy, str)
    assert isinstance(content.portfolio, list)
    assert len(content.portfolio) > 0
    for item in content.portfolio:
        assert item.asset not in (None, "", "null")
        assert isinstance(item.asset, str)
        assert item.percentage > 0
        assert item.percentage <= 100
        assert isinstance(item.percentage, (int, float))
        assert item.motivation not in (None, "", "null")
        assert isinstance(item.motivation, str)
    # La somma delle percentuali deve essere esattamente 100
    total_percentage = sum(item.percentage for item in content.portfolio)
    assert abs(total_percentage - 100) < 0.01  # Permette una piccola tolleranza per errori di arrotondamento

class TestPredictor:

    @pytest.fixture(scope="class")
    def inputs(self):
        data = []
        for symbol, price in [("BTC", 60000.00), ("ETH", 3500.00), ("SOL", 150.00)]:
            product_info = ProductInfo()
            product_info.symbol = symbol
            product_info.price = price
            data.append(product_info)

        return PredictorInput(data=data, style=PredictorStyle.AGGRESSIVE, sentiment="positivo")

    def test_gemini_model_output(self, inputs):
        unified_checks(AppModels.GEMINI, inputs)

    def test_ollama_qwen_model_output(self, inputs):
        unified_checks(AppModels.OLLAMA_QWEN, inputs)

    @pytest.mark.slow
    def test_ollama_gpt_oss_model_output(self, inputs):
        unified_checks(AppModels.OLLAMA_GPT, inputs)
