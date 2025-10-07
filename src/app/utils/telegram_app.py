import os
from enum import Enum
from typing import Any
from agno.utils.log import log_info  # type: ignore
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, User
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, ExtBot, JobQueue, CallbackQueryHandler, MessageHandler, filters
from app.models import AppModels
from app.predictor import PredictorStyle


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
    model_team: AppModels
    model_output: AppModels
    strategy: PredictorStyle

    def __init__(self):
        self.model_team = BotFunctions.app_models[0]
        self.model_output = BotFunctions.app_models[0]
        self.strategy = PredictorStyle.CONSERVATIVE



class BotFunctions:

    # In theory this is already thread-safe if run with CPython
    users_req: dict[User, ConfigsRun] = {}
    app_models: list[AppModels] = AppModels.availables()
    strategies: list[PredictorStyle] = list(PredictorStyle)

    # che incubo di typing
    @staticmethod
    def create_bot() -> Application[ExtBot[None], ContextTypes.DEFAULT_TYPE, dict[str, Any], dict[str, Any], dict[str, Any], JobQueue[ContextTypes.DEFAULT_TYPE]]:
        """
        Create a Telegram bot application instance.
        Assumes the TELEGRAM_BOT_TOKEN environment variable is set.
        Returns:
            Application: The Telegram bot application instance.
        Raises:
            AssertionError: If the TELEGRAM_BOT_TOKEN environment variable is not set.
        """

        token = os.getenv("TELEGRAM_BOT_TOKEN", '')
        assert token, "TELEGRAM_BOT_TOKEN environment variable not set"

        app = Application.builder().token(token).build()

        conv_handler = ConversationHandler(
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
        )

        app.add_handler(conv_handler)

        log_info("Telegram bot application created successfully.")
        return app

    ########################################
    # Funzioni di utilità
    ########################################
    @staticmethod
    async def start_message(user: User, query: CallbackQuery | Message) -> None:
        confs = BotFunctions.users_req.setdefault(user, ConfigsRun())

        str_model_team = f"{ConfigsChat.MODEL_TEAM.value}:                      {confs.model_team.name}"
        str_model_output = f"{ConfigsChat.MODEL_OUTPUT.value}:\t\t {confs.model_output.name}"
        str_strategy = f"{ConfigsChat.STRATEGY.value}:\t\t {confs.strategy.name}"

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

        models = [(m.name, f"__select_config:{state}:{m.name}") for m in BotFunctions.app_models]
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


    #########################################
    # Funzioni async per i comandi e messaggi
    #########################################
    @staticmethod
    async def __start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        message, user = await BotFunctions.handle_message(update)
        log_info(f"@{user.username} started the conversation.")
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

        strategies = [(s.name, f"__select_config:{ConfigsChat.STRATEGY}:{s.name}") for s in BotFunctions.strategies]
        inline_btns = [[InlineKeyboardButton(name, callback_data=callback_data)] for name, callback_data in strategies]

        await query.edit_message_text("Select a strategy", reply_markup=InlineKeyboardMarkup(inline_btns))
        return SELECT_CONFIG

    @staticmethod
    async def __select_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await BotFunctions.handle_callbackquery(update)
        log_info(f"@{user.username} --> {query.data}")

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
        msg2 = await message.reply_text("Elaborating your request...")

        confs = BotFunctions.users_req[user]
        log_info(f"@{user.username} started the team with [{confs.model_team}, {confs.model_output}, {confs.strategy}]")

        await BotFunctions.__run_team(confs, msg2)
        return ConversationHandler.END

    @staticmethod
    async def __cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query, user = await BotFunctions.handle_callbackquery(update)
        log_info(f"@{user.username} canceled the conversation.")
        if user in BotFunctions.users_req:
            del BotFunctions.users_req[user]
        await query.edit_message_text("Conversation canceled. Use /start to begin again.")
        return ConversationHandler.END

    @staticmethod
    async def __run_team(confs: ConfigsRun, msg: Message) -> None:
        # TODO fare il run effettivo del team
        import asyncio

        # Simulate a long-running task
        n_simulations = 3
        for i in range(n_simulations):
            await msg.edit_text(f"Working... {i+1}/{n_simulations}")
            await asyncio.sleep(2)
        await msg.edit_text("Team work completed.")




if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    bot_app = BotFunctions.create_bot()
    bot_app.run_polling()

