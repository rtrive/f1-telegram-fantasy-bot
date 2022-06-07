import requests  # type: ignore
from typing import Optional, Union

from requests import Response
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
)
from telegram.helpers import escape_markdown
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
        league_url = f"https://fantasy-api.formula1.com/f1/2022/leaderboards/leagues?v=1&league_id={league_id}"  # noqa: E501

        async def get_f1_fantasy_standings(
            update: Update, context: CallbackContext.DEFAULT_TYPE
        ):
            req = requests.get(
                url=league_url,
                headers={"Cookie": cookies},
            )
            standing_message = get_standings_as_string(req)
            # FIXME: At the moment the parse_mode has been set to MARKDOWN.
            # We have to decide how to show the standings
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=escape_markdown(f"```{standing_message}```", version=2),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        return get_f1_fantasy_standings


# TODO Define the format of the output message
def get_standings_as_string(req: Union[Response, Response]) -> str:
    status_code = req.status_code
    if status_code == 200:
        leaderboard = req.json()["leaderboard"]["leaderboard_entrants"]

        table = pt.PrettyTable(["Username", "Points"])
        for entry in leaderboard:
            table.add_row([entry["username"], entry["score"]])
        return f"```{table}```"
    else:
        return f"Ko with status code {status_code}"
