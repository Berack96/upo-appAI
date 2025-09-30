import gradio as gr

from dotenv import load_dotenv
from app.pipeline import Pipeline
from agno.utils.log import log_info

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

    pipeline = Pipeline()

    with gr.Blocks() as demo:
        gr.Markdown("# 🤖 Agente di Analisi e Consulenza Crypto")

        with gr.Row():
            provider = gr.Dropdown(
                choices=pipeline.list_providers(),
                type="index",
                label="Modello da usare"
            )
            provider.change(fn=pipeline.choose_provider, inputs=provider, outputs=None)

            style = gr.Dropdown(
                choices=pipeline.list_styles(),
                type="index",
                label="Stile di investimento"
            )
            style.change(fn=pipeline.choose_style, inputs=style, outputs=None)

        user_input = gr.Textbox(label="Richiesta utente")
        output = gr.Textbox(label="Risultato analisi", lines=12)

        analyze_btn = gr.Button("🔎 Analizza")
        analyze_btn.click(fn=pipeline.interact, inputs=[user_input], outputs=output)

    server, port = ("0.0.0.0", 8000)
    log_info(f"Starting UPO AppAI on http://{server}:{port}")
    demo.launch(server_name=server, server_port=port, quiet=True)
