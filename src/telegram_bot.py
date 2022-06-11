import logging
import prettytable as pt
import requests
from typing import Optional, Union, TypeVar, Callable
from requests import Response
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
)
from telegram.helpers import escape_markdown

from core.error import Error
from adapters.leaderboard_adapters import to_league_standings
from core.league_standing import LeagueStanding

T = TypeVar("T")

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, api_key: Optional[str]):
        try:
            self.application = ApplicationBuilder().token(api_key).build()
        except Exception as e:
            logger.error(e)

    def start_bot(self):
        try:
            self.application.run_polling()
        except Exception as e:
            logger.error(e)

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
            standings = decode_http_response(req, to_league_standings)

            if isinstance(standings, LeagueStanding):
                # TODO: We can improve this part as well
                table = pt.PrettyTable(["Username", "Points"])
                for entrant in standings.entrants:
                    table.add_row([entrant.user.username, entrant.score])
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=escape_markdown(f"{table}", version=2),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Non è stato possibile recuperare la classifica",
                )

        return get_f1_fantasy_standings


# TODO Move to utility package/file
def decode_http_response(
    req: Union[Response, Response], decode_fn: Callable[[dict], T]
) -> Union[Error, T]:
    status_code = req.status_code
    if status_code == 200:
        return decode_fn(req.json())
    else:
        return Error(req.json())
