# IMPORTANTE: Carichiamo le variabili d'ambiente PRIMA di qualsiasi altra cosa
import asyncio
import logging
from dotenv import load_dotenv
from app.configs import AppConfig
from app.interface import ChatManager, BotFunctions
from app.agents import Pipeline


if __name__ == "__main__":
    # Inizializzazioni
    load_dotenv()

    configs = AppConfig.load()
    pipeline = Pipeline(configs)

    chat = ChatManager()
    gradio = chat.gradio_build_interface()
    _app, local_url, share_url = gradio.launch(server_name="0.0.0.0", server_port=configs.port, quiet=True, prevent_thread_lock=True, share=configs.gradio_share)
    logging.info(f"UPO AppAI Chat is running on {share_url or local_url}")

    try:
        telegram = BotFunctions.create_bot(share_url)
        telegram.run_polling()
    except Exception as _:
        logging.warning("Telegram bot could not be started. Continuing without it.")
        asyncio.get_event_loop().run_forever()
    finally:
        gradio.close()
