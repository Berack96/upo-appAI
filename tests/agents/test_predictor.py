import json
import pytest
from app.agents import predictor
from app.models import Models

def unified_checks(model: Models, input):
    llm = model.get_agent(predictor.instructions())
    result = llm.run(input)

    print(result.content)
    potential_json = Models.extract_json_str_from_response(result.content)
    content = json.loads(potential_json)  # Verifica che l'output sia un JSON valido

    assert content['strategia'] is not None
    assert isinstance(content['portafoglio'], list)
    assert abs(sum(item['percentuale'] for item in content['portafoglio']) - 100) < 0.01  # La somma deve essere esattamente 100

class TestPredictor:

    @pytest.fixture(scope="class")
    def inputs(self):
        data = []
        for symbol, price in [("BTC", 60000.00), ("ETH", 3500.00), ("SOL", 150.00)]:
            product_info = predictor.ProductInfo()
            product_info.symbol = symbol
            product_info.price = price
            data.append(product_info)

        return predictor.prepare_inputs(
            data=data,
            style=predictor.PredictorStyle.AGGRESSIVE,
            sentiment="positivo"
        )

    def test_gemini_model_output(self, inputs):
        unified_checks(Models.GEMINI, inputs)

    @pytest.mark.slow
    def test_ollama_gpt_oss_model_output(self, inputs):
        unified_checks(Models.OLLAMA_GPT, inputs)

    def test_ollama_qwen_model_output(self, inputs):
        unified_checks(Models.OLLAMA_QWEN, inputs)
