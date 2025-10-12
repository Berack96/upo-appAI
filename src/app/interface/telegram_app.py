import io
import os
import json
import httpx
import logging
import warnings
from enum import Enum
from markdown_pdf import MarkdownPdf, Section
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, User
from telegram.constants import ChatAction
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from app.agents.pipeline import Pipeline
from app.configs import AppConfig

# per per_message di ConversationHandler che rompe sempre qualunque input tu metta
warnings.filterwarnings("ignore")
logging = logging.getLogger("telegram")


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

# Usato per separare la query arrivata da Telegram
QUERY_SEP = "|==|"

class ConfigsChat(Enum):
    MODEL_TEAM = "Team Model"
    MODEL_OUTPUT = "Output Model"
    STRATEGY = "Strategy"

class ConfigsRun:
    def __init__(self, configs: AppConfig):
        team, leader, strategy = configs.get_defaults()
        self.team_model = team
        self.leader_model = leader
        self.strategy = strategy
        self.user_query = ""


class TelegramApp:
    def __init__(self, pipeline: Pipeline):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        assert token, "TELEGRAM_BOT_TOKEN environment variable not set"

        self.user_requests: dict[User, ConfigsRun] = {}
        self.pipeline = pipeline
        self.token = token
        self.create_bot()

    def add_miniapp_url(self, url: str) -> None:
        try:
            endpoint = f"https://api.telegram.org/bot{self.token}/setChatMenuButton"
            payload = {"menu_button": json.dumps({
                "type": "web_app",
                "text": "MiniApp",
                "web_app": { "url": url }
            })}
            httpx.post(endpoint, data=payload)
        except httpx.HTTPError as e:
            logging.warning(f"Failed to update mini app URL: {e}")

    def create_bot(self) -> None:
        """
        Initialize the Telegram bot and set up the conversation handler.
        """
        app = Application.builder().token(self.token).build()

        app.add_error_handler(self.__error_handler)
        app.add_handler(ConversationHandler(
            per_message=False, # capire a cosa serve perchè da un warning quando parte il server
            entry_points=[CommandHandler('start', self.__start)],
            states={
                CONFIGS: [
                    CallbackQueryHandler(self.__model_team, pattern=ConfigsChat.MODEL_TEAM.name),
                    CallbackQueryHandler(self.__model_output, pattern=ConfigsChat.MODEL_OUTPUT.name),
                    CallbackQueryHandler(self.__strategy, pattern=ConfigsChat.STRATEGY.name),
                    CallbackQueryHandler(self.__cancel, pattern='^cancel$'),
                    MessageHandler(filters.TEXT, self.__start_team)  # Any text message
                ],
                SELECT_CONFIG: [
                    CallbackQueryHandler(self.__select_config, pattern=f"^__select_config{QUERY_SEP}.*$"),
                ]
            },
            fallbacks=[CommandHandler('start', self.__start)],
        ))
        self.app = app

    def run(self) -> None:
        self.app.run_polling()

    ########################################
    # Funzioni di utilità
    ########################################
    async def start_message(self, user: User, query: CallbackQuery | Message) -> None:
        confs = self.user_requests.setdefault(user, ConfigsRun(self.pipeline.configs))

        str_model_team = f"{ConfigsChat.MODEL_TEAM.value}:   {confs.team_model.label}"
        str_model_output = f"{ConfigsChat.MODEL_OUTPUT.value}:   {confs.leader_model.label}"
        str_strategy = f"{ConfigsChat.STRATEGY.value}:   {confs.strategy.label}"

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

    async def handle_callbackquery(self, update: Update) -> tuple[CallbackQuery, User]:
        assert update.callback_query and update.callback_query.from_user, "Update callback_query or user is None"
        query = update.callback_query
        await query.answer()  # Acknowledge the callback query
        return query, query.from_user

    async def handle_message(self, update: Update) -> tuple[Message, User]:
        assert update.message and update.message.from_user, "Update message or user is None"
        return update.message, update.message.from_user

    def callback_data(self, strings: list[str]) -> str:
        return QUERY_SEP.join(strings)

    async def __error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            logging.exception(f"Unhandled exception in Telegram handler {context.error}")

            # Try to notify the user in chat if possible
            if isinstance(update, Update) and update.effective_chat:
                chat_id = update.effective_chat.id
                msg = "Si è verificato un errore inatteso. Gli sviluppatori sono stati avvisati."
                await context.bot.send_message(chat_id=chat_id, text=msg)

        except Exception:
            # Ensure we never raise from the error handler itself
            logging.exception("Exception in the error handler")

    #########################################
    # Funzioni async per i comandi e messaggi
    #########################################
    async def __start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        message, user = await self.handle_message(update)
        logging.info(f"@{user.username} started the conversation.")
        await self.start_message(user, message)
        return CONFIGS

    async def __model_team(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await self._model_select(update, ConfigsChat.MODEL_TEAM)

    async def __model_output(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        return await self._model_select(update, ConfigsChat.MODEL_OUTPUT)

    async def _model_select(self, update: Update, state: ConfigsChat, msg: str | None = None) -> int:
        query, _ = await self.handle_callbackquery(update)

        models = [(m.label, self.callback_data([f"__select_config", str(state), m.name])) for m in self.pipeline.configs.models.all_models]
        inline_btns = [[InlineKeyboardButton(name, callback_data=callback_data)] for name, callback_data in models]

        await query.edit_message_text(msg or state.value, reply_markup=InlineKeyboardMarkup(inline_btns))
        return SELECT_CONFIG

    async def __strategy(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, _ = await self.handle_callbackquery(update)

        strategies = [(s.label, self.callback_data([f"__select_config", str(ConfigsChat.STRATEGY), s.name])) for s in self.pipeline.configs.strategies]
        inline_btns = [[InlineKeyboardButton(name, callback_data=callback_data)] for name, callback_data in strategies]

        await query.edit_message_text("Select a strategy", reply_markup=InlineKeyboardMarkup(inline_btns))
        return SELECT_CONFIG

    async def __select_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await self.handle_callbackquery(update)
        logging.debug(f"@{user.username} --> {query.data}")

        req = self.user_requests[user]
        _, state, model_name = str(query.data).split(QUERY_SEP)
        if state == str(ConfigsChat.MODEL_TEAM):
            req.team_model = self.pipeline.configs.get_model_by_name(model_name)
        if state == str(ConfigsChat.MODEL_OUTPUT):
            req.leader_model = self.pipeline.configs.get_model_by_name(model_name)
        if state == str(ConfigsChat.STRATEGY):
            req.strategy = self.pipeline.configs.get_strategy_by_name(model_name)

        await self.start_message(user, query)
        return CONFIGS

    async def __start_team(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        message, user = await self.handle_message(update)

        confs = self.user_requests[user]
        confs.user_query = message.text or ""

        logging.info(f"@{user.username} started the team with [{confs.team_model.label}, {confs.leader_model.label}, {confs.strategy.label}]")
        await self.__run_team(update, confs)

        logging.info(f"@{user.username} team finished.")
        return ConversationHandler.END

    async def __cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await self.handle_callbackquery(update)
        logging.info(f"@{user.username} canceled the conversation.")
        if user in self.user_requests:
            del self.user_requests[user]
        await query.edit_message_text("Conversation canceled. Use /start to begin again.")
        return ConversationHandler.END

    async def __run_team(self, update: Update, confs: ConfigsRun) -> None:
        if not update.message: return

        bot = update.get_bot()
        msg_id = update.message.message_id - 1
        chat_id = update.message.chat_id

        configs_str = [
            'Running with configurations:   ',
            f'Team:      {confs.team_model.label}',
            f'Output:    {confs.leader_model.label}',
            f'Strategy:  {confs.strategy.label}',
            f'Query:     "{confs.user_query}"'
        ]
        full_message = f"""```\n{'\n'.join(configs_str)}\n```\n\n"""
        msg = await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=full_message, parse_mode='MarkdownV2')
        if isinstance(msg, bool): return

        # Remove user query and bot message
        await bot.delete_message(chat_id=chat_id, message_id=update.message.id)

        self.pipeline.leader_model = confs.leader_model
        self.pipeline.team_model = confs.team_model
        self.pipeline.strategy = confs.strategy

        # TODO migliorare messaggi di attesa
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        report_content = self.pipeline.interact(confs.user_query)
        await msg.delete()

        # attach report file to the message
        pdf = MarkdownPdf(toc_level=2, optimize=True)
        pdf.add_section(Section(report_content, toc=False))

        # TODO vedere se ha senso dare il pdf o solo il messaggio
        document = io.BytesIO()
        pdf.save_bytes(document)
        document.seek(0)
        await bot.send_document(chat_id=chat_id, document=document, filename="report.pdf", parse_mode='MarkdownV2', caption=full_message)

