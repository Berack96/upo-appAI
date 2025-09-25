import gradio as gr

from dotenv import load_dotenv
from app.tool import ToolAgent
from app.models import Models

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

    list_models = Models.available()
    tool_agent = ToolAgent()

    with gr.Blocks() as demo:
        gr.Markdown("# 🤖 Agente di Analisi e Consulenza Crypto")

        with gr.Row():
            provider = gr.Dropdown(
                choices=list_models,
                value=list_models[0],
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

