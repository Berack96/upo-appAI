import os
import json
import gradio as gr
from app.agents.pipeline import Pipeline, PipelineInputs


class ChatManager:
    """
    Gestisce la conversazione con la Pipeline:
    - mantiene lo storico dei messaggi
    - invoca la Pipeline per generare risposte
    - salva e ricarica le chat
    """

    def __init__(self):
        self.history: list[dict[str, str]] = []  # [{"role": "user"/"assistant", "content": "..."}]
        self.inputs = PipelineInputs()

    def send_message(self, message: str) -> None:
        """
        Aggiunge un messaggio utente, chiama la Pipeline e salva la risposta nello storico.
        """
        # Aggiungi messaggio utente allo storico
        self.history.append({"role": "user", "content": message})

    def receive_message(self, response: str) -> str:
        """
        Riceve un messaggio dalla pipeline e lo aggiunge allo storico.
        """
        # Aggiungi risposta assistente allo storico
        self.history.append({"role": "assistant", "content": response})

        return response

    def save_chat(self, filename: str = "chat.json") -> None:
        """
        Salva la chat corrente in src/saves/<filename>.
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def load_chat(self, filename: str = "chat.json") -> None:
        """
        Carica una chat salvata da src/saves/<filename>.
        """
        if not os.path.exists(filename):
            self.history = []
            return
        with open(filename, "r", encoding="utf-8") as f:
            self.history = json.load(f)

    def reset_chat(self) -> None:
        """
        Resetta lo storico della chat.
        """
        self.history = []

    def get_history(self) -> list[dict[str, str]]:
        """
        Restituisce lo storico completo della chat.
        """
        return self.history


    ########################################
    # Funzioni Gradio
    ########################################
    def gradio_respond(self, message: str, history: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]], str]:
        self.send_message(message)

        self.inputs.user_query = message
        pipeline = Pipeline(self.inputs)
        response = pipeline.interact()

        self.receive_message(response)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})
        return history, history, ""

    def gradio_save(self) -> str:
        self.save_chat("chat.json")
        return "💾 Chat salvata in chat.json"

    def gradio_load(self) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        self.load_chat("chat.json")
        history: list[dict[str, str]] = []
        for m in self.get_history():
            history.append({"role": m["role"], "content": m["content"]})
        return history, history

    def gradio_clear(self) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        self.reset_chat()
        return [], []

    def gradio_build_interface(self) -> gr.Blocks:
        with gr.Blocks() as interface:
            gr.Markdown("# 🤖 Agente di Analisi e Consulenza Crypto (Chat)")

            # Dropdown provider e stile
            with gr.Row():
                provider = gr.Dropdown(
                    choices=self.inputs.list_models_names(),
                    type="index",
                    label="Modello da usare"
                )
                provider.change(fn=self.inputs.choose_team_leader, inputs=provider, outputs=None)

                style = gr.Dropdown(
                    choices=self.inputs.list_strategies_names(),
                    type="index",
                    label="Stile di investimento"
                )
                style.change(fn=self.inputs.choose_strategy, inputs=style, outputs=None)

            chatbot = gr.Chatbot(label="Conversazione", height=500, type="messages")
            msg = gr.Textbox(label="Scrivi la tua richiesta", placeholder="Es: Quali sono le crypto interessanti oggi?")

            with gr.Row():
                clear_btn = gr.Button("🗑️ Reset Chat")
                save_btn = gr.Button("💾 Salva Chat")
                load_btn = gr.Button("📂 Carica Chat")

            # Eventi e interazioni
            msg.submit(self.gradio_respond, inputs=[msg, chatbot], outputs=[chatbot, chatbot, msg])
            clear_btn.click(self.gradio_clear, inputs=None, outputs=[chatbot, chatbot])
            save_btn.click(self.gradio_save, inputs=None, outputs=None)
            load_btn.click(self.gradio_load, inputs=None, outputs=[chatbot, chatbot])

        return interface