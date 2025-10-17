'''
print("Raccolta modelli disponibili: ")
from app.models import AppModels
available_models = AppModels.availables()
print("Modelli disponibili: ")
for model in available_models:
    model_name = model.name
    print(f"Modello {model_name} disponibile.")
    try:
        agent = model.get_agent(instructions="Rispondi in maniera concisa e semplice.")
        result = agent.run("Che modello sei?").content
        print(f"Risposta di {model_name}: {result}")
    except Exception as e:
        print(f"Si sono verificati degli errori con il modello {model_name}")
'''

from app.models import AppModels
available_models = AppModels.availables()
def general_test(model: AppModels):
    agent = model.get_agent(instructions="Rispondi in maniera concisa e semplice.")
    result = agent.run("Che modello sei?").content
    assert result is not None
def test_gemini():
    model = AppModels.GEMINI
    general_test(model)
def test_gemini_pro():
    model = AppModels.GEMINI_PRO
    general_test(model)
def test_gpt():
    model = AppModels.GPT_4
    general_test(model)
def test_deepseek():
    model = AppModels.DEEPSEEK
    general_test(model)
def test_ollama_gpt():
    model = AppModels.OLLAMA_GPT
    general_test(model)
def test_ollama_qwen():
    model = AppModels.OLLAMA_QWEN
    general_test(model)
def test_ollama_qwen_4B():
    model = AppModels.OLLAMA_QWEN_4B
    general_test(model)
def test_ollama_qwen_1B():
    model = AppModels.OLLAMA_QWEN_1B
    general_test(model)
