import asyncio
import logging
from dotenv import load_dotenv
from app.configs import AppConfig
from app.interface import *


if __name__ == "__main__":
    # =====================
    load_dotenv()
    configs = AppConfig.load()
    # =====================

    chat = ChatManager()
    gradio = chat.gradio_build_interface()
    _app, local_url, share_url = gradio.launch(server_name="0.0.0.0", server_port=configs.port, quiet=True, prevent_thread_lock=True, share=configs.gradio_share)
    logging.info(f"UPO AppAI Chat is running on {share_url or local_url}")

    try:
        telegram = TelegramApp()
        telegram.add_miniapp_url(share_url)
        telegram.run()
    except AssertionError as e:
        try:
            logging.warning(f"Telegram bot could not be started: {e}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down due to KeyboardInterrupt")
    finally:
        gradio.close()
