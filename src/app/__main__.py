import gradio as gr
from dotenv import load_dotenv
from agno.utils.log import log_info #type: ignore
from app.utils import ChatManager
from app.agents import Pipeline
from app.utils.telegram_app import BotFunctions


# Disabilita TUTTI i log di livello inferiore a WARNING
# La maggior parte arrivano da httpx
import logging
logging.getLogger().setLevel(logging.WARNING)



def gradio_app(pipeline: Pipeline, server: str = "0.0.0.0", port: int = 8000) -> str:
    chat = ChatManager()

    ########################################
    # Funzioni Gradio
    ########################################
    def respond(message: str, history: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]], str]:
        chat.send_message(message)
        response = pipeline.interact(message)
        chat.receive_message(response)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        return history, history, ""

    def save_current_chat() -> str:
        chat.save_chat("chat.json")
        return "💾 Chat salvata in chat.json"

    def load_previous_chat() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        chat.load_chat("chat.json")
        history: list[dict[str, str]] = []
        for m in chat.get_history():
            history.append({"role": m["role"], "content": m["content"]})
        return history, history

    def reset_chat() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        chat.reset_chat()
        return [], []

    ########################################
    # Interfaccia Gradio
    ########################################
    with gr.Blocks() as demo:
        gr.Markdown("# 🤖 Agente di Analisi e Consulenza Crypto (Chat)")

        # Dropdown provider e stile
        with gr.Row():
            provider = gr.Dropdown(
                choices=pipeline.list_providers(),
                type="index",
                label="Modello da usare"
            )
            provider.change(fn=pipeline.choose_predictor, inputs=provider, outputs=None)

            style = gr.Dropdown(
                choices=pipeline.list_styles(),
                type="index",
                label="Stile di investimento"
            )
            style.change(fn=pipeline.choose_style, inputs=style, outputs=None)

        chatbot = gr.Chatbot(label="Conversazione", height=500, type="messages")
        msg = gr.Textbox(label="Scrivi la tua richiesta", placeholder="Es: Quali sono le crypto interessanti oggi?")

        with gr.Row():
            clear_btn = gr.Button("🗑️ Reset Chat")
            save_btn = gr.Button("💾 Salva Chat")
            load_btn = gr.Button("📂 Carica Chat")

        # Eventi e interazioni
        msg.submit(respond, inputs=[msg, chatbot], outputs=[chatbot, chatbot, msg])
        clear_btn.click(reset_chat, inputs=None, outputs=[chatbot, chatbot])
        save_btn.click(save_current_chat, inputs=None, outputs=None)
        load_btn.click(load_previous_chat, inputs=None, outputs=[chatbot, chatbot])

    _app, local, share = demo.launch(server_name=server, server_port=port, quiet=True, prevent_thread_lock=True)
    log_info(f"UPO AppAI Chat is running on {local} and {share}")
    return share



if __name__ == "__main__":
    load_dotenv()  # Carica le variabili d'ambiente dal file .env

    pipeline = Pipeline()
    url = gradio_app(pipeline)

    telegram = BotFunctions.create_bot(pipeline, url)
    telegram.run_polling()

