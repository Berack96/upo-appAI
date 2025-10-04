import gradio as gr
from agno.utils.log import log_info #type: ignore
from dotenv import load_dotenv
from app import ChatManager


if __name__ == "__main__":
    # Inizializzazioni
    load_dotenv()
    chat = ChatManager()

    ########################################
    # Funzioni Gradio
    ########################################
    def respond(message: str, history: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]], str]:
        response = chat.send_message(message)
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
                choices=chat.list_providers(),
                type="index",
                label="Modello da usare"
            )
            provider.change(fn=chat.choose_provider, inputs=provider, outputs=None)

            style = gr.Dropdown(
                choices=chat.list_styles(),
                type="index",
                label="Stile di investimento"
            )
            style.change(fn=chat.choose_style, inputs=style, outputs=None)

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

    server, port = ("0.0.0.0", 8000) # 0.0.0.0 per accesso esterno (Docker)
    server_log = "localhost" if server == "0.0.0.0" else server
    log_info(f"Starting UPO AppAI Chat on http://{server_log}:{port}") # noqa
    demo.launch(server_name=server, server_port=port, quiet=True)
