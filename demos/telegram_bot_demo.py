import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Esempio di funzione per gestire il comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message: return
    await update.message.reply_text('Ciao! Inviami un messaggio e ti risponderò!')


# Esempio di funzione per fare echo del messaggio ricevuto
async def echo(update: Update,  context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message: return

    print(f"Ricevuto messaggio: {message.text} da chat id: {message.chat.id}")
    await message.reply_text(text=f"Hai detto: {message.text}")


# Esempio di funzione per far partire una inline keyboard (comando /keyboard)
async def inline_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message: return
    keyboard = [
        [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose:', reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query: return
    await query.answer()
    await query.edit_message_text(text=f"Selected option: {query.data}")





def main():
    print("Bot in ascolto...")

    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN", '')
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("keyboard", inline_keyboard))
    app.add_handler(MessageHandler(filters=filters.TEXT, callback=echo))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()