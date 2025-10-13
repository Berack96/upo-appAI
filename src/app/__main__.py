import asyncio
import logging
from dotenv import load_dotenv
from app.configs import AppConfig
from app.interface import *
from app.agents import Pipeline


if __name__ == "__main__":
    load_dotenv()

    configs = AppConfig.load()
    pipeline = Pipeline(configs)

    chat = ChatManager(pipeline)
    gradio = chat.gradio_build_interface()
    _app, local_url, share_url = gradio.launch(server_name="0.0.0.0", server_port=configs.port, quiet=True, prevent_thread_lock=True, share=configs.gradio_share)
    logging.info(f"UPO AppAI Chat is running on {share_url or local_url}")

    try:
        telegram = TelegramApp(pipeline)
        telegram.add_miniapp_url(share_url)
        telegram.run()
    except AssertionError as e:
        try:
            logging.warning(f"Telegram bot could not be started: {e}")
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down due to KeyboardInterrupt")
    finally:
        gradio.close()
