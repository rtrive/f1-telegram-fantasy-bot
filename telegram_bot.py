import requests  # type: ignore
from typing import Optional
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
)
import prettytable as pt


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
    def get_standings(cookies: str, league_id: str):
        async def standings(update: Update, context: CallbackContext.DEFAULT_TYPE):
            req = requests.get(
                url=f'https://fantasy-api.formula1.com/f1/2022/leaderboards/leagues?v=1&league_id={league_id}',
                headers={"Cookie": cookies},
            )
            if req.status_code == 200:
                leaderboard = req.json()['leaderboard']['leaderboard_entrants']

                table = pt.PrettyTable(['Team', 'Points'])
                for entry in leaderboard:
                    table.add_row([entry['team_name'], entry['score']])
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f'```{table}```', parse_mode=ParseMode.MARKDOWN_V2)
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f"Ko with status {req.status_code}"
                )

        return standings
