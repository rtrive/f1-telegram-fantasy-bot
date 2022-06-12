import datetime
import requests  # type: ignore
import logging
from typing import Optional, Union, TypeVar, Callable
from requests import Response
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
)
from telegram.helpers import escape_markdown

from adapters.leaderboard_adapters import (
    to_league_standings,
    league_standing_to_pretty_table,
)
from adapters.season_adapters import to_races
from core.error import Error

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
            f1_fantasy_standings_req = requests.get(
                url=league_url,
                headers={"Cookie": cookies},
            )
            standings = decode_http_response(
                f1_fantasy_standings_req, to_league_standings
            )
            if isinstance(standings, Error):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Non è stato possibile recuperare la classifica",
                )
            else:
                message = league_standing_to_pretty_table(standing=standings)
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=escape_markdown(f"{message}", version=2),
                    parse_mode=ParseMode.MARKDOWN_V2,
                )

        return get_f1_fantasy_standings

    @staticmethod
    def get_last_race_standing(cookies: str, league_id: str, now: datetime.datetime):
        async def get_last_f1_fantasy_race_standing(
            update: Update, context: CallbackContext.DEFAULT_TYPE
        ):
            default_error_message = "Non è stato possibile recuperare la classifica"
            req = requests.get(
                url="https://fantasy-api.formula1.com/f1/2022?v=1",
                headers={"Cookie": cookies},
            )

            season_races = decode_http_response(req, to_races)

            if isinstance(season_races, Error):
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=default_error_message
                )
            else:
                last_race_list = list(
                    filter(
                        lambda race: race.start_timestamp < now
                        and race.status == "results",
                        season_races,
                    )
                )

                if not last_race_list:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id, text=default_error_message
                    )
                else:
                    last_race = last_race_list.pop()

                    last_race_standings_req = requests.get(
                        url=f"https://fantasy-api.formula1.com/f1/2022/leaderboards/leagues?v=1&game_period_id={last_race.id}&league_id={league_id}",  # noqa: E501
                        headers={"Cookie": cookies},
                    )

                    last_race_standings = decode_http_response(
                        last_race_standings_req, to_league_standings
                    )
                    if isinstance(last_race_standings, Error):
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id, text=default_error_message
                        )
                    else:
                        message = league_standing_to_pretty_table(
                            standing=last_race_standings
                        )
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=escape_markdown(f"{message}", version=2),
                            parse_mode=ParseMode.MARKDOWN_V2,
                        )

        return get_last_f1_fantasy_race_standing


# TODO Move to utility package/file
def decode_http_response(
    req: Union[Response, Response], decode_fn: Callable[[dict], T]
) -> Union[Error, T]:
    status_code = req.status_code
    if status_code == 200:
        return decode_fn(req.json())
    else:
        return Error(req.json())
