import datetime
from typing import List

import requests  # type: ignore

from adapters.leaderboard_adapters import (
    entrant_to_pretty_input,
    league_standing_to_pretty_table,
    to_league_standings,
)
from adapters.picked_player_adapters import (
    picker_players_to_pretty_table,
    to_picked_players,
)
from adapters.season_adapters import to_races
from bot.telegram_command import (
    COMMANDS,
    TELEGRAM_FANTASY_LAST_GP_STANDING_COMMAND,
    TELEGRAM_FANTASY_STANDING_COMMAND,
    TELEGRAM_FANTASY_TEAM_COMMAND,
    TELEGRAM_HELP_COMMAND,
    TELEGRAM_START_COMMAND,
)
from core.error import Error
from telegram import InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Handler
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
            url=f"https://fantasy-api.formula1.com/f1/2022/leaderboards/leagues?v=1&league_id={league_id}",  # noqa: E501
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
                    url=f"https://fantasy-api.formula1.com/f1/2022/leaderboards/leagues?v=1&game_period_id={last_race.id}&league_id={league_id}",  # noqa: E501
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


def get_last_race_team_standing_handler(cookies: str, league_id: str):
    def get_f1_last_race_team_standing_handler(
        update: Update, context: CallbackContext
    ) -> None:
        f1_fantasy_standings_req = requests.get(
            url=f"https://fantasy-api.formula1.com/f1/2022/leaderboards/leagues?v=1&league_id={league_id}",  # noqa: E501
            headers={"Cookie": cookies},
        )
        standings = decode_http_response(f1_fantasy_standings_req, to_league_standings)
        inputs = entrant_to_pretty_input(standings)
        reply_markup = InlineKeyboardMarkup(inputs)

        update.message.reply_text("Please choose:", reply_markup=reply_markup)

    return get_f1_last_race_team_standing_handler


def get_last_race_team_standing_handler_button(cookies: str, now: datetime.datetime):
    def get_f1_last_race_team_standing_handler_button(
        update: Update, context: CallbackContext
    ) -> None:

        query = update.callback_query

        query.answer()
        user_global_id = query.data

        req = requests.get(
            url="https://fantasy-api.formula1.com/f1/2022?v=1",
            headers={"Cookie": cookies},
        )

        season_races = decode_http_response(req, to_races)

        last_race_list = list(
            filter(
                lambda race: race.start_timestamp < now and race.status == "results",
                season_races,
            )
        )
        last_race = last_race_list.pop()

        f1_fantasy_standing_team_req = requests.get(
            url=f"https://fantasy-api.formula1.com/f1/2022/picked_teams/for_slot?v=1&game_period_id={last_race.id}&slot=1&user_global_id={user_global_id}",  # noqa: E501
            headers={"Cookie": cookies},
        )
        picked_players = decode_http_response(
            f1_fantasy_standing_team_req, to_picked_players
        )
        message = picker_players_to_pretty_table(picker_players=picked_players)
        message.title = last_race.name

        query.edit_message_text(
            text=f"<pre>{message}</pre>",
            parse_mode=ParseMode.HTML,
        )

    return get_f1_last_race_team_standing_handler_button


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
        CommandHandler(
            TELEGRAM_FANTASY_TEAM_COMMAND,
            get_last_race_team_standing_handler(cookies=cookies, league_id=league_id),
        ),
        CallbackQueryHandler(
            get_last_race_team_standing_handler_button(
                cookies=cookies, now=datetime.datetime.now()
            )
        ),
    ]
