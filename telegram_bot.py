import requests  # type: ignore
from typing import Optional
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
)


class Bot:
    def __init__(self, api_key: Optional[str]):
        try:
            self.application = ApplicationBuilder().token(api_key).build()
        except Exception as e:
            print(e)

    def start_bot(self):
        try:
            self.application.run_polling()
        except Exception as e:
            print(e)

    @staticmethod
    def start_bot_handler():
        async def start(update: Update, context: CallbackContext.DEFAULT_TYPE):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="I'm a F1 Fantasy bot, please talk to me!",
            )
        return start

    @staticmethod
    def echo_handler():
        async def echo(update: Update, context: CallbackContext.DEFAULT_TYPE):
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=update.message.text
            )
        return echo

    @staticmethod
    def get_standings(cookies: str):
        async def standings(update: Update, context: CallbackContext.DEFAULT_TYPE):
            req = requests.get(
                url="https://fantasy-api.formula1.com/f1/2022/league_entrants?v=1",
                headers={"Cookie": cookies},
            )
            print(req.json())
        return standings
