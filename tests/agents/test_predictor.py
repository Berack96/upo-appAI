import pytest
from app.agents import AppModels
from app.agents.predictor import PREDICTOR_INSTRUCTIONS, PredictorInput, PredictorOutput, PredictorStyle
from app.base.markets import ProductInfo

def unified_checks(model: AppModels, input: PredictorInput) -> None:
    llm = model.get_agent(PREDICTOR_INSTRUCTIONS, output_schema=PredictorOutput) # type: ignore[arg-type]
    result = llm.run(input) # type: ignore
    content = result.content

    assert isinstance(content, PredictorOutput)
    assert content.strategy not in (None, "", "null")
    assert isinstance(content.strategy, str)
    assert isinstance(content.portfolio, list)
    assert len(content.portfolio) > 0
    for item in content.portfolio:
        assert item.asset not in (None, "", "null")
        assert isinstance(item.asset, str)
        assert item.percentage >= 0.0
        assert item.percentage <= 100.0
        assert isinstance(item.percentage, (int, float))
        assert item.motivation not in (None, "", "null")
        assert isinstance(item.motivation, str)
    # La somma delle percentuali deve essere esattamente 100
    total_percentage = sum(item.percentage for item in content.portfolio)
    assert abs(total_percentage - 100) < 0.01  # Permette una piccola tolleranza per errori di arrotondamento

class TestPredictor:

    def inputs(self) -> PredictorInput:
        data: list[ProductInfo] = []
        for symbol, price in [("BTC", 60000.00), ("ETH", 3500.00), ("SOL", 150.00)]:
            product_info = ProductInfo()
            product_info.symbol = symbol
            product_info.price = price
            data.append(product_info)

        return PredictorInput(data=data, style=PredictorStyle.AGGRESSIVE, sentiment="positivo")

    def test_gemini_model_output(self):
        inputs = self.inputs()
        unified_checks(AppModels.GEMINI, inputs)

    def test_ollama_qwen_1b_model_output(self):
        inputs = self.inputs()
        unified_checks(AppModels.OLLAMA_QWEN_1B, inputs)

    def test_ollama_qwen_4b_model_output(self):
        inputs = self.inputs()
        unified_checks(AppModels.OLLAMA_QWEN_4B, inputs)

    @pytest.mark.slow
    def test_ollama_qwen_latest_model_output(self):
        inputs = self.inputs()
        unified_checks(AppModels.OLLAMA_QWEN, inputs)

    @pytest.mark.slow
    def test_ollama_gpt_oss_model_output(self):
        inputs = self.inputs()
        unified_checks(AppModels.OLLAMA_GPT, inputs)
