import gradio as gr

from dotenv import load_dotenv
from app.tool import ToolAgent
from app.models import Models
from app.agents.predictor import PredictorStyle

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

    models = Models.availables()
    styles = list(PredictorStyle)
    models_names = [model.name for model in models]
    styles_names = [style.value for style in styles]
    print("✅ Modelli disponibili:", models_names)
    print("✅ Stili disponibili:", styles_names)

    tool_agent = ToolAgent(models, styles)

    with gr.Blocks() as demo:
        gr.Markdown("# 🤖 Agente di Analisi e Consulenza Crypto")

        with gr.Row():
            provider = gr.Dropdown(
                choices=models_names,
                type="index",
                label="Modello da usare"
            )
            provider.change(fn=tool_agent.choose_provider, inputs=provider, outputs=None)

            style = gr.Dropdown(
                choices=styles_names,
                type="index",
                label="Stile di investimento"
            )

        user_input = gr.Textbox(label="Richiesta utente")
        output = gr.Textbox(label="Risultato analisi", lines=12)

        analyze_btn = gr.Button("🔎 Analizza")
        analyze_btn.click(fn=tool_agent.interact, inputs=[user_input, style], outputs=output)
    demo.launch()
