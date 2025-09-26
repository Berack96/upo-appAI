import gradio as gr

from dotenv import load_dotenv
from app.tool import ToolAgent

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
            provider = gr.Dropdown(
                choices=tool_agent.list_providers(),
                type="index",
                label="Modello da usare"
            )
            provider.change(fn=tool_agent.choose_provider, inputs=provider, outputs=None)

            style = gr.Dropdown(
                choices=tool_agent.list_styles(),
                type="index",
                label="Stile di investimento"
            )

        user_input = gr.Textbox(label="Richiesta utente")
        output = gr.Textbox(label="Risultato analisi", lines=12)

        analyze_btn = gr.Button("🔎 Analizza")
        analyze_btn.click(fn=tool_agent.interact, inputs=[user_input, style], outputs=output)
    demo.launch(server_name="0.0.0.0", server_port=8000)
