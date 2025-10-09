# IMPORTANTE: Carichiamo le variabili d'ambiente PRIMA di qualsiasi altra cosa
from dotenv import load_dotenv
load_dotenv()



# IMPORTARE LIBRERIE DA QUI IN POI
from app.utils import ChatManager, BotFunctions
from agno.utils.log import log_info #type: ignore




if __name__ == "__main__":
    server, port, share = ("0.0.0.0", 8000, False) # TODO Temp configs, maybe read from env/yaml/ini file later

    chat = ChatManager()
    gradio = chat.gradio_build_interface()
    _app, local_url, share_url = gradio.launch(server_name=server, server_port=port, quiet=True, prevent_thread_lock=True, share=share)
    log_info(f"UPO AppAI Chat is running on {local_url} and {share_url}")

    telegram = BotFunctions.create_bot(share_url)
    telegram.run_polling()

