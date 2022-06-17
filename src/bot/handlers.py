import datetime
from typing import List

import requests
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, Handler, CommandHandler

from adapters.leaderboard_adapters import (
    league_standing_to_pretty_table,
    to_league_standings,
)
from adapters.season_adapters import to_races
from bot.telegram_command import COMMANDS, TELEGRAM_START_COMMAND, TELEGRAM_HELP_COMMAND, \
    TELEGRAM_FANTASY_STANDING_COMMAND, TELEGRAM_FANTASY_LAST_GP_STANDING_COMMAND, TELEGRAM_FANTASY_REMIND_BEFORE_GP
from core.error import Error
from utils.http import decode_http_response


def help_bot_handler():
    def help_message(update: Update, context: CallbackContext):
        help_msg = "I can help you with F1 Fantasy information. My commands are:\n\n"
        for command in filter(lambda c: c.active is True, COMMANDS):
            help_msg += f"/{command.name} - {command.description}\n"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=help_msg,
        )

    return help_message


def get_standings_handler(cookies: str, league_id: str):
    def get_f1_fantasy_standings(update: Update, context: CallbackContext):
        f1_fantasy_standings_req = requests.get(
            url=f"https://fantasy-api.formula1.com/f1/2022/leaderboards/leagues?v=1&league_id={league_id}",
            # noqa: E501,
            headers={"Cookie": cookies},
        )
        standings = decode_http_response(f1_fantasy_standings_req, to_league_standings)
        if isinstance(standings, Error):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="It wasn't possible to retrieve the standing",
            )
        else:
            message = league_standing_to_pretty_table(standing=standings)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"<pre>{message}</pre>",
                parse_mode=ParseMode.HTML,
            )

    return get_f1_fantasy_standings


def get_last_race_standing_handler(
    cookies: str, league_id: str, now: datetime.datetime
):
    def get_last_f1_fantasy_race_standing(update: Update, context: CallbackContext):
        default_error_message = "It wasn't possible to retrieve the standing"
        req = requests.get(
            url="https://fantasy-api.formula1.com/f1/2022?v=1",
            headers={"Cookie": cookies},
        )

        season_races = decode_http_response(req, to_races)

        if isinstance(season_races, Error):
            context.bot.send_message(
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
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=default_error_message
                )
            else:
                last_race = last_race_list.pop()

                last_race_standings_req = requests.get(
                    url=f"https://fantasy-api.formula1.com/f1/2022/leaderboards/leagues?v=1&game_period_id={last_race.id}&league_id={league_id}",
                    # noqa: E501
                    headers={"Cookie": cookies},
                )

                last_race_standings = decode_http_response(
                    last_race_standings_req, to_league_standings
                )
                if isinstance(last_race_standings, Error):
                    context.bot.send_message(
                        chat_id=update.effective_chat.id, text=default_error_message
                    )
                else:
                    message = league_standing_to_pretty_table(
                        standing=last_race_standings
                    )
                    message.title = last_race.name
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"<pre>{message}</pre>",
                        parse_mode=ParseMode.HTML,
                    )

    return get_last_f1_fantasy_race_standing


def set_timer_handler():
    def set_lineup_reminders(update: Update, context: CallbackContext) -> None:

        """Add a job to the queue."""
        chat_id = update.message.chat_id
        try:
            # args[0] should contain the time for the timer in seconds
            due = int(context.args[0])
            if due < 0:
                update.message.reply_text("Sorry we can not go back to future!")
                return

            job_removed = remove_job_if_exists(str(chat_id), context)
            context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

            text = "Timer successfully set!"
            if job_removed:
                text += " Old one was removed."
            update.message.reply_text(text)

        except (IndexError, ValueError):
            update.message.reply_text("Usage: /set <seconds>")

    return set_lineup_reminders


# FIXME: find a way to use what is in telegram_command.py to avoid duplication
def get_handlers(cookies: str, league_id: str) -> List[Handler]:
    return [
        CommandHandler(
            [TELEGRAM_START_COMMAND, TELEGRAM_HELP_COMMAND],
            help_bot_handler(),
        ),
        CommandHandler(
            TELEGRAM_FANTASY_STANDING_COMMAND,
            get_standings_handler(cookies=cookies, league_id=league_id),
        ),
        CommandHandler(
            TELEGRAM_FANTASY_LAST_GP_STANDING_COMMAND,
            get_last_race_standing_handler(
                cookies=cookies, league_id=league_id, now=datetime.datetime.now()
            ),
        ),
        CommandHandler(TELEGRAM_FANTASY_REMIND_BEFORE_GP, set_timer_handler()),
    ]


# This means that the function you are attempting to schedule has one of the following problems:
#
# It is a lambda function (e.g. lambda x: x + 1)
# It is a bound method (function tied to a particular instance of some class)
# It is a nested function (function inside another function)
# You are trying to schedule a function that is not tied to any actual module
# (such as a function defined in the REPL, hence __main__ as the module name)
def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text="Beep!")


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True
