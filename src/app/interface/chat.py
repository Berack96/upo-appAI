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
        self.history: list[tuple[str, str]] = []  
        self.inputs = PipelineInputs()

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

    def get_history(self) -> list[tuple[str, str]]:
        """
        Restituisce lo storico completo della chat.
        """
        return self.history


    ########################################
    # Funzioni Gradio
    ########################################
    def gradio_respond(self, message: str, history: list[tuple[str, str]]) -> str:
        self.inputs.user_query = message
        pipeline = Pipeline(self.inputs)
        response = pipeline.interact()

        self.history.append((message, response))
        return response

    def gradio_save(self) -> str:
        self.save_chat("chat.json")
        return "💾 Chat salvata in chat.json"

    def gradio_load(self) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
        self.load_chat("chat.json")
        history = self.get_history()
        return history, history

    def gradio_clear(self) -> tuple[list[str], list[str]]:
        self.reset_chat()
        return [], []


    def gradio_build_interface(self) -> gr.Blocks:
        with gr.Blocks() as interface:
            gr.Markdown("# 🤖 Agente di Analisi e Consulenza Crypto (Chat)")

            # Dropdown provider e stile
            with gr.Row():
                provider = gr.Dropdown(
                    choices=self.inputs.list_models_names(),
                    value=self.inputs.team_leader_model.label,
                    type="index",
                    label="Modello da usare"
                )
                provider.change(fn=self.inputs.choose_team_leader, inputs=provider, outputs=None)
                provider.value = self.inputs.team_leader_model.label

                strategy = gr.Dropdown(
                    choices=self.inputs.list_strategies_names(),
                    value=self.inputs.strategy.label,
                    type="index",
                    label="Stile di investimento"
                )
                strategy.change(fn=self.inputs.choose_strategy, inputs=strategy, outputs=None)
                strategy.value = self.inputs.strategy.label

            chat = gr.ChatInterface(
                fn=self.gradio_respond
            )

            with gr.Row():
                clear_btn = gr.Button("🗑️ Reset Chat")
                save_btn = gr.Button("💾 Salva Chat")
                load_btn = gr.Button("📂 Carica Chat")

            clear_btn.click(self.gradio_clear, inputs=None, outputs=[chat.chatbot, chat.chatbot_state])
            save_btn.click(self.gradio_save, inputs=None, outputs=None)
            load_btn.click(self.gradio_load, inputs=None, outputs=[chat.chatbot, chat.chatbot_state])
        return interface
