import io
import os
import json
import httpx
import logging
import warnings
from enum import Enum
from typing import Any
from markdown_pdf import MarkdownPdf, Section
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, User
from telegram.constants import ChatAction
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, ExtBot, JobQueue, MessageHandler, filters
from app.agents.pipeline import Pipeline

# per per_message di ConversationHandler che rompe sempre qualunque input tu metta
warnings.filterwarnings("ignore")
logging = logging.getLogger(__name__)


# Lo stato cambia in base al valore di ritorno delle funzioni async
# END state è già definito in telegram.ext.ConversationHandler
# Un semplice schema delle interazioni:
#      /start
#         ║
#         V
#  ╔══ CONFIGS <═════╗
#  ║      ║ ╚══> SELECT_CONFIG
#  ║      V
#  ║  start_team (polling for updates)
#  ║      ║
#  ║      V
#  ╚═══> END
CONFIGS, SELECT_CONFIG = range(2)

class ConfigsChat(Enum):
    MODEL_TEAM = "Team Model"
    MODEL_OUTPUT = "Output Model"
    STRATEGY = "Strategy"

class ConfigsRun:
    def __init__(self):
        self.model_team = Pipeline.available_models[0]
        self.model_output = Pipeline.available_models[0]
        self.strategy = Pipeline.all_styles[0]
        self.user_query = ""



class BotFunctions:

    # In theory this is already thread-safe if run with CPython
    users_req: dict[User, ConfigsRun]

    # che incubo di typing
    @staticmethod
    def create_bot(miniapp_url: str | None = None) -> Application[ExtBot[None], ContextTypes.DEFAULT_TYPE, dict[str, Any], dict[str, Any], dict[str, Any], JobQueue[ContextTypes.DEFAULT_TYPE]]:
        """
        Create a Telegram bot application instance.
        Assumes the TELEGRAM_BOT_TOKEN environment variable is set.
        Returns:
            Application: The Telegram bot application instance.
        Raises:
            AssertionError: If the TELEGRAM_BOT_TOKEN environment variable is not set.
        """
        BotFunctions.users_req = {}

        token = os.getenv("TELEGRAM_BOT_TOKEN", '')
        assert token, "TELEGRAM_BOT_TOKEN environment variable not set"

        if miniapp_url: BotFunctions.update_miniapp_url(miniapp_url, token)
        app = Application.builder().token(token).build()

        app.add_handler(ConversationHandler(
            per_message=False, # capire a cosa serve perchè da un warning quando parte il server
            entry_points=[CommandHandler('start', BotFunctions.__start)],
            states={
                CONFIGS: [
                    CallbackQueryHandler(BotFunctions.__model_team, pattern=ConfigsChat.MODEL_TEAM.name),
                    CallbackQueryHandler(BotFunctions.__model_output, pattern=ConfigsChat.MODEL_OUTPUT.name),
                    CallbackQueryHandler(BotFunctions.__strategy, pattern=ConfigsChat.STRATEGY.name),
                    CallbackQueryHandler(BotFunctions.__cancel, pattern='^cancel$'),
                    MessageHandler(filters.TEXT, BotFunctions.__start_team)  # Any text message
                ],
                SELECT_CONFIG: [
                    CallbackQueryHandler(BotFunctions.__select_config, pattern='^__select_config:.*$'),
                ]
            },
            fallbacks=[CommandHandler('start', BotFunctions.__start)],
        ))
        return app

    ########################################
    # Funzioni di utilità
    ########################################
    @staticmethod
    async def start_message(user: User, query: CallbackQuery | Message) -> None:
        confs = BotFunctions.users_req.setdefault(user, ConfigsRun())

        str_model_team = f"{ConfigsChat.MODEL_TEAM.value}:   {confs.model_team.name}"
        str_model_output = f"{ConfigsChat.MODEL_OUTPUT.value}:   {confs.model_output.name}"
        str_strategy = f"{ConfigsChat.STRATEGY.value}:   {confs.strategy.name}"

        msg, keyboard = (
            "Please choose an option or write your query",
            InlineKeyboardMarkup([
                [InlineKeyboardButton(str_model_team, callback_data=ConfigsChat.MODEL_TEAM.name)],
                [InlineKeyboardButton(str_model_output, callback_data=ConfigsChat.MODEL_OUTPUT.name)],
                [InlineKeyboardButton(str_strategy, callback_data=ConfigsChat.STRATEGY.name)],
                [InlineKeyboardButton("Cancel", callback_data='cancel')]
            ])
        )

        if isinstance(query, CallbackQuery):
            await query.edit_message_text(msg, reply_markup=keyboard, parse_mode='MarkdownV2')
        else:
            await query.reply_text(msg, reply_markup=keyboard, parse_mode='MarkdownV2')

    @staticmethod
    async def handle_configs(update: Update, state: ConfigsChat, msg: str | None = None) -> int:
        query, _ = await BotFunctions.handle_callbackquery(update)

        models = [(m.name, f"__select_config:{state}:{m.name}") for m in Pipeline.available_models]
        inline_btns = [[InlineKeyboardButton(name, callback_data=callback_data)] for name, callback_data in models]

        await query.edit_message_text(msg or state.value, reply_markup=InlineKeyboardMarkup(inline_btns))
        return SELECT_CONFIG

    @staticmethod
    async def handle_callbackquery(update: Update) -> tuple[CallbackQuery, User]:
        assert update.callback_query and update.callback_query.from_user, "Update callback_query or user is None"
        query = update.callback_query
        await query.answer()  # Acknowledge the callback query
        return query, query.from_user

    @staticmethod
    async def handle_message(update: Update) -> tuple[Message, User]:
        assert update.message and update.message.from_user, "Update message or user is None"
        return update.message, update.message.from_user

    @staticmethod
    def update_miniapp_url(url: str, token: str) -> None:
        try:
            endpoint = f"https://api.telegram.org/bot{token}/setChatMenuButton"
            payload = {"menu_button": json.dumps({
                "type": "web_app",
                "text": "MiniApp",
                "web_app": {
                    "url": url
                }
            })}
            httpx.post(endpoint, data=payload)
        except httpx.HTTPError as e:
            logging.info(f"Failed to update mini app URL: {e}")

    #########################################
    # Funzioni async per i comandi e messaggi
    #########################################
    @staticmethod
    async def __start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        message, user = await BotFunctions.handle_message(update)
        logging.info(f"@{user.username} started the conversation.")
        await BotFunctions.start_message(user, message)
        return CONFIGS

    @staticmethod
    async def __model_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await BotFunctions.handle_configs(update, ConfigsChat.MODEL_TEAM)

    @staticmethod
    async def __model_output(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await BotFunctions.handle_configs(update, ConfigsChat.MODEL_OUTPUT)

    @staticmethod
    async def __strategy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, _ = await BotFunctions.handle_callbackquery(update)

        strategies = [(s.name, f"__select_config:{ConfigsChat.STRATEGY}:{s.name}") for s in Pipeline.all_styles]
        inline_btns = [[InlineKeyboardButton(name, callback_data=callback_data)] for name, callback_data in strategies]

        await query.edit_message_text("Select a strategy", reply_markup=InlineKeyboardMarkup(inline_btns))
        return SELECT_CONFIG

    @staticmethod
    async def __select_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await BotFunctions.handle_callbackquery(update)
        logging.info(f"@{user.username} --> {query.data}")

        req = BotFunctions.users_req[user]

        _, state, model_name = str(query.data).split(':')
        if state == str(ConfigsChat.MODEL_TEAM):
            req.model_team = AppModels[model_name]
        if state == str(ConfigsChat.MODEL_OUTPUT):
            req.model_output = AppModels[model_name]
        if state == str(ConfigsChat.STRATEGY):
            req.strategy = PredictorStyle[model_name]

        await BotFunctions.start_message(user, query)
        return CONFIGS

    @staticmethod
    async def __start_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        message, user = await BotFunctions.handle_message(update)

        confs = BotFunctions.users_req[user]
        confs.user_query = message.text or ""

        logging.info(f"@{user.username} started the team with [{confs.model_team}, {confs.model_output}, {confs.strategy}]")
        await BotFunctions.__run_team(update, confs)

        logging.info(f"@{user.username} team finished.")
        return ConversationHandler.END

    @staticmethod
    async def __cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await BotFunctions.handle_callbackquery(update)
        logging.info(f"@{user.username} canceled the conversation.")
        if user in BotFunctions.users_req:
            del BotFunctions.users_req[user]
        await query.edit_message_text("Conversation canceled. Use /start to begin again.")
        return ConversationHandler.END

    @staticmethod
    async def __run_team(update: Update, confs: ConfigsRun) -> None:
        if not update.message: return

        bot = update.get_bot()
        msg_id = update.message.message_id - 1
        chat_id = update.message.chat_id

        configs_str = [
            'Running with configurations:   ',
            f'Team:      {confs.model_team.name}',
            f'Output:    {confs.model_output.name}',
            f'Strategy:  {confs.strategy.name}',
            f'Query:     "{confs.user_query}"'
        ]
        full_message = f"""```\n{'\n'.join(configs_str)}\n```\n\n"""
        msg = await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=full_message, parse_mode='MarkdownV2')
        if isinstance(msg, bool): return

        # Remove user query and bot message
        await bot.delete_message(chat_id=chat_id, message_id=update.message.id)

        # TODO settare correttamente i modelli
        pipeline = Pipeline()
        #pipeline.choose_predictor(Pipeline.available_models.index(confs.model_team))
        pipeline.choose_style(Pipeline.all_styles.index(confs.strategy))

        # TODO migliorare messaggi di attesa
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        report_content = pipeline.interact(confs.user_query)
        await msg.delete()

        # attach report file to the message
        pdf = MarkdownPdf(toc_level=2, optimize=True)
        pdf.add_section(Section(report_content, toc=False))

        # TODO vedere se ha senso dare il pdf o solo il messaggio
        document = io.BytesIO()
        pdf.save_bytes(document)
        document.seek(0)
        await bot.send_document(chat_id=chat_id, document=document, filename="report.pdf", parse_mode='MarkdownV2', caption=full_message)

