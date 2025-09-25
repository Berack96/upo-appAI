import os
import gradio as gr

from dotenv import load_dotenv
from app.tool import ToolAgent

def available_keys():
    """
    Controlla quali provider di modelli LLM hanno le loro API keys disponibili
    come variabili d'ambiente e ritorna una lista di provider disponibili.
    Se nessuna API key è disponibile, ritorna solo 'mock' come opzione.
    """
    availables = []
    if os.getenv("GOOGLE_API_KEY"):
        availables.append("google")
    if os.getenv("OPENAI_API_KEY"):
        availables.append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        availables.append("anthropic")
    if os.getenv("DEEPSEEK_API_KEY"):
        availables.append("deepseek")
    if os.getenv("OLLAMA_MODELS_PATH"):
        availables.append("ollama")

    return ['mock', *availables]


########################################
# MAIN APP & GRADIO INTERFACE
########################################
if __name__ == "__main__":
    ######################################
    # DA FARE PRIMA DI ESEGUIRE L'APP
    # qui carichiamo le variabili d'ambiente dal file .env
    # una volta fatto, possiamo usare le API keys senza problemi
    # quindi non è necessario richiamare load_dotenv() altrove
    load_dotenv()
    ######################################

    tool_agent = ToolAgent()

    with gr.Blocks() as demo:
        gr.Markdown("# 🤖 Agente di Analisi e Consulenza Crypto")

        with gr.Row():
            list_choices = available_keys()
            provider = gr.Dropdown(
                choices=list_choices,
                value=list_choices[0],
                label="Modello da usare"
            )
            style = gr.Dropdown(
                choices=["conservative", "aggressive"],
                value="conservative",
                label="Stile di investimento"
            )

        user_input = gr.Textbox(label="Richiesta utente")
        output = gr.Textbox(label="Risultato analisi", lines=12)

        analyze_btn = gr.Button("🔎 Analizza")
        analyze_btn.click(fn=tool_agent.interact, inputs=[user_input, provider, style], outputs=output)
    if __name__ == "__main__":
        demo.launch()

