from telegram.ext import Application


class Bot:

    def __init__(self, api_key: str):
        self.application = Application.builder().token(api_key).build()
