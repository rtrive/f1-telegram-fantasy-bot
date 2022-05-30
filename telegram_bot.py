from telegram import Update
from telegram.ext import (
    filters,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
)


async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a F1 Fantasy bot, please talk to me!"
    )


async def echo(update: Update, context: CallbackContext.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=update.message.text
    )


class Bot:
    def __init__(self, api_key: str):
        try:
            self.application = ApplicationBuilder().token(api_key).build()
            start_handler = CommandHandler("start", start)
            echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
            self.application.add_handler(start_handler)
            self.application.add_handler(echo_handler)
            self.application.run_polling()
        except Exception as e:
            print(e)
