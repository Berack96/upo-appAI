import asyncio
import io
import os
import json
from typing import Any
import httpx
import logging
import warnings
from enum import Enum
from markdown_pdf import MarkdownPdf, Section
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, User
from telegram.constants import ChatAction
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from app.agents.pipeline import Pipeline, PipelineEvent, PipelineInputs, RunMessage

# per per_message di ConversationHandler che rompe sempre qualunque input tu metta
warnings.filterwarnings("ignore")
logging = logging.getLogger("telegram")


# Lo stato cambia in base al valore di ritorno delle funzioni async
# END state è già definito in telegram.ext.ConversationHandler
# Un semplice schema delle interazioni:
#      /start
#         ║
#         v
#  ╔══ CONFIGS <═════╗
#  ║      ║ ╚══> SELECT_CONFIG
#  ║      v          ^
#  ║    MODELS ══════╝
#  ║
#  ╠══> start (polling for updates)
#  ║      ║
#  ║      v
#  ╚═══> END
CONFIGS, SELECT_MODEL, SELECT_CONFIG = range(3)

# Usato per separare la query arrivata da Telegram
QUERY_SEP = "|==|"

class ConfigsChat(Enum):
    MODEL_CHECK = "Check Model"
    MODEL_TEAM_LEADER = "Team Leader Model"
    MODEL_TEAM = "Team Model"
    MODEL_REPORT = "Report Model"
    CHANGE_MODELS = "Change Models"
    STRATEGY = "Strategy"
    CANCEL = "Cancel"

    def get_inline_button(self, value_to_display:str="") -> InlineKeyboardButton:
        display = self.value if not value_to_display else f"{self.value}:   {value_to_display}"
        return InlineKeyboardButton(display, callback_data=self.name)

    def change_value(self, inputs: PipelineInputs, new_value:int) -> None:
        if self.name == self.MODEL_CHECK.name:
            inputs.choose_query_checker(new_value)
        elif self.name == self.MODEL_TEAM_LEADER.name:
            inputs.choose_team_leader(new_value)
        elif self.name == self.MODEL_TEAM.name:
            inputs.choose_team(new_value)
        elif self.name == self.MODEL_REPORT.name:
            inputs.choose_report_generator(new_value)
        elif self.name == self.STRATEGY.name:
            inputs.choose_strategy(new_value)


class TelegramApp:
    def __init__(self):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        assert token, "TELEGRAM_BOT_TOKEN environment variable not set"

        self.user_requests: dict[User, PipelineInputs] = {}
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
                    CallbackQueryHandler(self.__models, pattern=ConfigsChat.CHANGE_MODELS.name),
                    CallbackQueryHandler(self.__strategy, pattern=ConfigsChat.STRATEGY.name),
                    CallbackQueryHandler(self.__cancel, pattern='^CANCEL$'),
                    MessageHandler(filters.TEXT, self.__start_llms)  # Any text message
                ],
                SELECT_MODEL: [
                    CallbackQueryHandler(self.__model_select, pattern=ConfigsChat.MODEL_CHECK.name),
                    CallbackQueryHandler(self.__model_select, pattern=ConfigsChat.MODEL_TEAM_LEADER.name),
                    CallbackQueryHandler(self.__model_select, pattern=ConfigsChat.MODEL_TEAM.name),
                    CallbackQueryHandler(self.__model_select, pattern=ConfigsChat.MODEL_REPORT.name),
                    CallbackQueryHandler(self.__go_to_start, pattern='^CANCEL$'),
                ],
                SELECT_CONFIG: [
                    CallbackQueryHandler(self.__select_config, pattern=f"^__select_config{QUERY_SEP}.*$"),
                    CallbackQueryHandler(self.__go_to_start, pattern='^CANCEL$'),
                ]
            },
            fallbacks=[CommandHandler('start', self.__start)],
        ))
        self.app = app

    def run(self) -> None:
        """
        Start the Telegram bot polling. This will keep the bot running and listening for updates.\n
        This function blocks until the bot is stopped.
        """
        self.app.run_polling()

    ########################################
    # Funzioni di utilità
    ########################################
    async def handle_callbackquery(self, update: Update) -> tuple[CallbackQuery, User]:
        assert update.callback_query, "Update callback_query is None"
        assert update.effective_user, "Update effective_user is None"
        query = update.callback_query
        await query.answer()  # Acknowledge the callback query
        return query, update.effective_user

    def handle_message(self, update: Update) -> tuple[Message, User]:
        assert update.message and update.effective_user, "Update message or user is None"
        return update.message, update.effective_user

    def build_callback_data(self, callback: str, config: ConfigsChat, labels: list[str]) -> list[tuple[str, str]]:
        return [(label, QUERY_SEP.join((callback, config.name, str(i)))) for i, label in enumerate(labels)]

    async def __error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            logging.error(f"Unhandled exception in Telegram handler: {context.error}")

            # Try to notify the user in chat if possible
            if isinstance(update, Update) and update.effective_chat:
                chat_id = update.effective_chat.id
                msg = "An error occurred while processing your request."
                await context.bot.send_message(chat_id=chat_id, text=msg)

        except Exception:
            # Ensure we never raise from the error handler itself
            logging.exception("Exception in the error handler")

    #########################################
    # Funzioni base di gestione stati
    #########################################
    async def __start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user.username if update.effective_user else "Unknown"
        logging.info(f"@{user} started the conversation.")
        return await self.__go_to_start(update, context)

    async def __go_to_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        assert user, "Update effective_user is None"
        msg = update.callback_query if update.callback_query else update.message
        assert msg, "Update message and callback_query are both None"

        confs = self.user_requests.setdefault(user, PipelineInputs()) # despite the name, it creates a default only if not present
        args: dict[str, Any] = {
            "text": "Please choose an option or write your query",
            "parse_mode": 'MarkdownV2',
            "reply_markup": InlineKeyboardMarkup([
                [ConfigsChat.CHANGE_MODELS.get_inline_button()],
                [ConfigsChat.STRATEGY.get_inline_button(confs.strategy.label)],
                [ConfigsChat.CANCEL.get_inline_button()],
            ])
        }

        await (msg.edit_message_text(**args) if isinstance(msg, CallbackQuery) else msg.reply_text(**args))
        return CONFIGS

    async def __cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await self.handle_callbackquery(update)
        logging.info(f"@{user.username} canceled the conversation.")
        if user in self.user_requests:
            del self.user_requests[user]
        await query.edit_message_text("Conversation canceled. Use /start to begin again.")
        return ConversationHandler.END

    ##########################################
    # Configurazioni
    ##########################################
    async def __models(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await self.handle_callbackquery(update)
        req = self.user_requests[user]

        await query.edit_message_text("Select a model", reply_markup=InlineKeyboardMarkup([
            [ConfigsChat.MODEL_CHECK.get_inline_button(req.query_analyzer_model.label)],
            [ConfigsChat.MODEL_TEAM_LEADER.get_inline_button(req.team_leader_model.label)],
            [ConfigsChat.MODEL_TEAM.get_inline_button(req.team_model.label)],
            [ConfigsChat.MODEL_REPORT.get_inline_button(req.report_generation_model.label)],
            [ConfigsChat.CANCEL.get_inline_button()]
        ]))
        return SELECT_MODEL

    async def __model_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await self.handle_callbackquery(update)

        if not query.data:
            logging.error("Callback query data is None")
            return CONFIGS

        req = self.user_requests[user]
        models = self.build_callback_data("__select_config", ConfigsChat[query.data], req.list_models_names())
        inline_btns = [[InlineKeyboardButton(name, callback_data=callback_data)] for name, callback_data in models]

        await query.edit_message_text("Select a model", reply_markup=InlineKeyboardMarkup(inline_btns))
        return SELECT_CONFIG

    async def __strategy(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await self.handle_callbackquery(update)

        req = self.user_requests[user]
        strategies = self.build_callback_data("__select_config", ConfigsChat.STRATEGY, req.list_strategies_names())
        inline_btns = [[InlineKeyboardButton(name, callback_data=callback_data)] for name, callback_data in strategies]

        await query.edit_message_text("Select a strategy", reply_markup=InlineKeyboardMarkup(inline_btns))
        return SELECT_CONFIG

    async def __select_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await self.handle_callbackquery(update)
        logging.debug(f"@{user.username} --> {query.data}")

        req = self.user_requests[user]
        _, state, index = str(query.data).split(QUERY_SEP)
        ConfigsChat[state].change_value(req, int(index))

        return await self.__go_to_start(update, context)

    async def __start_llms(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        message, user = self.handle_message(update)

        confs = self.user_requests[user]
        confs.user_query = message.text or ""

        logging.info(f"@{user.username} started the team with [{confs.query_analyzer_model.label}, {confs.team_model.label}, {confs.team_leader_model.label}, {confs.report_generation_model.label}, {confs.strategy.label}]")
        await self.__run(update, confs)

        logging.info(f"@{user.username} team finished.")
        return ConversationHandler.END


    ##########################################
    # RUN APP
    ##########################################
    async def __run(self, update: Update, inputs: PipelineInputs) -> None:
        if not update.message: return

        bot = update.get_bot()
        msg_id = update.message.message_id - 1
        chat_id = update.message.chat_id

        run_message = RunMessage(inputs, prefix="```\n", suffix="\n```")
        msg = await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=run_message.get_latest(), parse_mode='MarkdownV2')
        if isinstance(msg, bool): return

        # Remove user query and bot message
        await bot.delete_message(chat_id=chat_id, message_id=update.message.id)

        def update_user(update: bool = True, extra: str = "") -> None:
            if update: run_message.update()
            message = run_message.get_latest(extra)
            if msg.text != message:
                asyncio.create_task(msg.edit_text(message, parse_mode='MarkdownV2'))

        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        pipeline = Pipeline(inputs)
        report_content = await pipeline.interact_async(listeners=[
            (PipelineEvent.QUERY_CHECK, lambda _: update_user()),
            (PipelineEvent.TOOL_USED, lambda e: update_user(False, f"`{e.agent_name} {e.tool.tool_name}`")),
            (PipelineEvent.INFO_RECOVERY, lambda _: update_user()),
            (PipelineEvent.REPORT_GENERATION, lambda _: update_user()),
        ])

        # attach report file to the message
        pdf = MarkdownPdf(toc_level=2, optimize=True)
        pdf.add_section(Section(report_content, toc=False))

        document = io.BytesIO()
        pdf.save_bytes(document)
        document.seek(0)
        await msg.reply_document(document=document, filename="report.pdf")
