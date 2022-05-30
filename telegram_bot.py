from typing import Optional
from telegram import Update
from telegram.ext import (
    filters,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
)


class Bot:
    def __init__(self, api_key: Optional[str], cookies: dict, url: str):
        try:
            self.cookies = cookies
            self.url = url
            self.application = ApplicationBuilder().token(api_key).build()
            start_handler = CommandHandler("start", self.start)
            echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.echo)
            self.application.add_handler(start_handler)
            self.application.add_handler(echo_handler)
            self.application.run_polling()
        except Exception as e:
            print(e)

    async def start(self, update: Update, context: CallbackContext.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="I'm a F1 Fantasy bot, please talk to me!",
        )

    async def echo(self, update: Update, context: CallbackContext.DEFAULT_TYPE):
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=update.message.text
        )
