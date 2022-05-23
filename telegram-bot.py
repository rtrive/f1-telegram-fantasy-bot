from os import getenv
from telegram.ext import Application


TOKEN = getenv("TELEGRAM_BOT_API_KEY")


class Bot():
    def __init__(self):
        self.application = Application.builder().token(TOKEN).build()
