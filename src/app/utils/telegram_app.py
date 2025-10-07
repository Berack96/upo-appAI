import os
from enum import Enum
from typing import Any
from agno.utils.log import log_info  # type: ignore
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, User
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, ExtBot, JobQueue, CallbackQueryHandler
from app.models import AppModels
from app.predictor import PredictorStyle


# conversation states
class ConfigStates(Enum):
    MODEL_TEAM = "Team Model"
    MODEL_OUTPUT = "Output Model"
    STRATEGY = "Strategy"

# conversation stages (checkpoints)
class Checkpoints(Enum):
    CONFIGS = 1
    TEAM_RUNNING = 2
    END = 3

class RunConfigs:
    model_team: AppModels
    model_output: AppModels
    strategy: PredictorStyle

    def __init__(self):
        self.model_team = AppModels.OLLAMA_QWEN_1B
        self.model_output = AppModels.OLLAMA_QWEN_1B
        self.strategy = PredictorStyle.CONSERVATIVE

class BotFunctions:

    # In theory this is already thread-safe if run with CPython
    users_req: dict[User, RunConfigs] = {}
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
            entry_points=[CommandHandler('start', BotFunctions.__start)],
            states={
                Checkpoints.CONFIGS: [
                    CallbackQueryHandler(BotFunctions.__model_team, pattern=ConfigStates.MODEL_TEAM.name),
                    CallbackQueryHandler(BotFunctions.__model_output, pattern=ConfigStates.MODEL_OUTPUT.name),
                    CallbackQueryHandler(BotFunctions.__strategy, pattern=ConfigStates.STRATEGY.name),
                    CallbackQueryHandler(BotFunctions.__next, pattern='^__next'),
                    CallbackQueryHandler(BotFunctions.__cancel, pattern='^cancel$')
                ],
                Checkpoints.TEAM_RUNNING: [],
                Checkpoints.END: [
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
        confs = BotFunctions.users_req.setdefault(user, RunConfigs())

        str_model_team = f"{ConfigStates.MODEL_TEAM.value}:\t\t {confs.model_team.name}"
        str_model_output = f"{ConfigStates.MODEL_OUTPUT.value}:\t\t {confs.model_output.name}"
        str_strategy = f"{ConfigStates.STRATEGY.value}:\t\t {confs.strategy.name}"

        msg, keyboard = (
            "Please choose an option or write your query",
            InlineKeyboardMarkup([
                [InlineKeyboardButton(str_model_team, callback_data=ConfigStates.MODEL_TEAM.name)],
                [InlineKeyboardButton(str_model_output, callback_data=ConfigStates.MODEL_OUTPUT.name)],
                [InlineKeyboardButton(str_strategy, callback_data=ConfigStates.STRATEGY.name)],
                [InlineKeyboardButton("Cancel", callback_data='cancel')]
            ])
        )

        if isinstance(query, CallbackQuery):
            await query.edit_message_text(msg, reply_markup=keyboard, parse_mode='MarkdownV2')
        else:
            await query.reply_text(msg, reply_markup=keyboard, parse_mode='MarkdownV2')

    @staticmethod
    async def handle_configs(update: Update, state: ConfigStates, msg: str | None = None) -> Checkpoints:
        query, _ = await BotFunctions.handle_callbackquery(update)

        models = [(m.name, f"__next:{state}:{m.name}") for m in BotFunctions.app_models]
        inline_btns = [[InlineKeyboardButton(name, callback_data=callback_data)] for name, callback_data in models]

        await query.edit_message_text(msg or state.value, reply_markup=InlineKeyboardMarkup(inline_btns))
        return Checkpoints.CONFIGS

    @staticmethod
    async def handle_callbackquery(update: Update) -> tuple[CallbackQuery, User]:
        assert update.callback_query and update.callback_query.from_user, "Update callback_query or user is None"
        query = update.callback_query
        await query.answer()  # Acknowledge the callback query
        return query, query.from_user


    #########################################
    # Funzioni async per i comandi e messaggi
    #########################################
    @staticmethod
    async def __start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Checkpoints:
        assert update.message and update.message.from_user, "Update message or user is None"
        user = update.message.from_user
        log_info(f"@{user.username} started the conversation.")
        await BotFunctions.start_message(user, update.message)
        return Checkpoints.CONFIGS

    @staticmethod
    async def __cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Checkpoints:
        query, user = await BotFunctions.handle_callbackquery(update)
        log_info(f"@{user.username} canceled the conversation.")
        if user in BotFunctions.users_req:
            del BotFunctions.users_req[user]
        await query.edit_message_text("Conversation canceled. Use /start to begin again.")
        return Checkpoints.END

    @staticmethod
    async def __model_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Checkpoints:
        return await BotFunctions.handle_configs(update, ConfigStates.MODEL_TEAM)

    @staticmethod
    async def __model_output(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Checkpoints:
        return await BotFunctions.handle_configs(update, ConfigStates.MODEL_OUTPUT)

    @staticmethod
    async def __strategy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Checkpoints:
        query, _ = await BotFunctions.handle_callbackquery(update)

        strategies = [(s.name, f"__next:{ConfigStates.STRATEGY}:{s.name}") for s in BotFunctions.strategies]
        inline_btns = [[InlineKeyboardButton(name, callback_data=callback_data)] for name, callback_data in strategies]

        await query.edit_message_text("Select a strategy", reply_markup=InlineKeyboardMarkup(inline_btns))
        return Checkpoints.CONFIGS

    @staticmethod
    async def __next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Checkpoints:
        query, user = await BotFunctions.handle_callbackquery(update)
        log_info(f"@{user.username} --> {query.data}")

        req = BotFunctions.users_req[user]

        _, state, model_name = str(query.data).split(':')
        if state == str(ConfigStates.MODEL_TEAM):
            req.model_team = AppModels[model_name]
        if state == str(ConfigStates.MODEL_OUTPUT):
            req.model_output = AppModels[model_name]
        if state == str(ConfigStates.STRATEGY):
            req.strategy = PredictorStyle[model_name]

        await BotFunctions.start_message(user, query)
        return Checkpoints.CONFIGS

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    bot_app = BotFunctions.create_bot()
    bot_app.run_polling()

