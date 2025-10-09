# IMPORTANTE: Carichiamo le variabili d'ambiente PRIMA di qualsiasi altra cosa
from dotenv import load_dotenv
load_dotenv()


# Modifico il comportamento del logging (dato che ci sono molte librerie che lo usano)
import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False, # Mantiene i logger esistenti (es. di terze parti)
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)s%(reset)s [%(asctime)s] (%(name)s) - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored',
            'level': 'INFO'
        },
    },
    'root': {  # Configura il logger root
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'httpx': {'level': 'WARNING'}, # Troppo spam per INFO
    }
})



# IMPORTARE LIBRERIE DA QUI IN POI
from app.utils import ChatManager, BotFunctions




if __name__ == "__main__":
    server, port, share = ("0.0.0.0", 8000, False) # TODO Temp configs, maybe read from env/yaml/ini file later

    chat = ChatManager()
    gradio = chat.gradio_build_interface()
    _app, local_url, share_url = gradio.launch(server_name=server, server_port=port, quiet=True, prevent_thread_lock=True, share=share)
    logging.info(f"UPO AppAI Chat is running on {local_url} and {share_url}")

    telegram = BotFunctions.create_bot(share_url)
    telegram.run_polling()

