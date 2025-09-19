import gradio as gr
from app.tool import ToolAgent

tool_agent = ToolAgent()

def analyze_request(user_input, provider, style):
    try:
        return tool_agent.interact(user_input, provider=provider, style=style)
    except Exception as e:
        return f"❌ Errore: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("# 🤖 Agente di Analisi e Consulenza Crypto")

    with gr.Row():
        provider = gr.Dropdown(
            choices=["mock", "openai", "anthropic", "google", "deepseek", "ollama"],
            value="mock",
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
    analyze_btn.click(fn=analyze_request, inputs=[user_input, provider, style], outputs=output)

if __name__ == "__main__":
    demo.launch()

