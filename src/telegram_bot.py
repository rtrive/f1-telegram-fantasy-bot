import datetime
import logging
from typing import Callable, List, Optional, TypeVar, Union

import constants
import requests  # type: ignore

from adapters.leaderboard_adapters import (
    league_standing_to_pretty_table,
    to_league_standings,
)
from adapters.season_adapters import to_races
from core.error import Error
from requests import Response
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    filters,
    Handler,
    MessageHandler,
)
from telegram.helpers import escape_markdown

T = TypeVar("T")

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, api_key: Optional[str], logger: logging.Logger):
        try:
            self.application = ApplicationBuilder().token(api_key).build()
        except Exception as e:
            logger.error(e)

    def start_bot(self):
        try:
            self.application.run_polling()
        except Exception as e:
            logger.error(e)

    def get_handlers(self, cookies: str, league_id: str) -> List[Handler]:
        return [
            CommandHandler(constants.TELEGRAM_START_COMMAND, self.help_bot_handler()),
            CommandHandler(constants.TELEGRAM_HELP_COMMAND, self.help_bot_handler()),
            MessageHandler(filters.TEXT & (~filters.COMMAND), self.echo_handler()),
            CommandHandler(
                constants.TELEGRAM_FANTASY_STANDING_COMMAND,
                self.get_standings_handler(cookies=cookies, league_id=league_id),
            ),
            CommandHandler(
                constants.TELEGRAM_FANTASY_LAST_GP_STANDING_COMMAND,
                self.get_last_race_standing_handler(
                    cookies=cookies, league_id=league_id, now=datetime.datetime.now()
                ),
            ),
        ]

    @staticmethod
    def start_bot_handler():
        return Bot.help_bot_handler()

    @staticmethod
    def help_bot_handler():
        async def help_message(update: Update, context: CallbackContext.DEFAULT_TYPE):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"I can help you with F1 Fantasy information. My commands are:\n\n"
                f"/{constants.TELEGRAM_FANTASY_STANDING_COMMAND} - Get the F1 Fantasy "
                f"standing\n"
                f"/{constants.TELEGRAM_FANTASY_LAST_GP_STANDING_COMMAND} - Get the F1 "
                f"Fantasy standing related to"
                f" the last completed GP",
            )

        return help_message

    @staticmethod
    def echo_handler():
        async def echo(update: Update, context: CallbackContext.DEFAULT_TYPE):
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=update.message.text
            )

        return echo

    @staticmethod
    def get_standings_handler(cookies: str, league_id: str):
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
                    text="It wasn't possible to retrieve the standing",
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
    def get_last_race_standing_handler(
        cookies: str, league_id: str, now: datetime.datetime
    ):
        async def get_last_f1_fantasy_race_standing(
            update: Update, context: CallbackContext.DEFAULT_TYPE
        ):
            default_error_message = "It wasn't possible to retrieve the standing"
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
                        message.title = last_race.name
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
