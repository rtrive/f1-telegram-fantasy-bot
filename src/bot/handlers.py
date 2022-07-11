import datetime
import logging
from typing import List

from adapters.leaderboard_adapters import (
    entrant_to_pretty_input,
    league_standing_to_pretty_table,
)
from adapters.picked_player_adapters import picked_players_to_pretty_table
from bot.telegram_command import (
    COMMANDS,
    TELEGRAM_FANTASY_LAST_GP_STANDING_COMMAND,
    TELEGRAM_FANTASY_LINEUP_REMINDER,
    TELEGRAM_FANTASY_STANDING_COMMAND,
    TELEGRAM_FANTASY_TEAM_COMMAND,
    TELEGRAM_HELP_COMMAND,
    TELEGRAM_START_COMMAND,
)
from core.error import Error
from services.f1_fantasy_service import F1FantasyService

from telegram import InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Handler

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


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


def get_standings_handler(f1_fantasy_service: F1FantasyService):
    def get_f1_fantasy_standings(update: Update, context: CallbackContext):
        league_standing = f1_fantasy_service.get_league_standing()
        if isinstance(league_standing, Error):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="It wasn't possible to retrieve the standing",
            )
        else:
            message = league_standing_to_pretty_table(standing=league_standing)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"<pre>{message}</pre>",
                parse_mode=ParseMode.HTML,
            )

    return get_f1_fantasy_standings


def get_last_race_standing_handler(
    now: datetime.datetime,
    f1_fantasy_service: F1FantasyService,
):
    def get_last_f1_fantasy_race_standing(update: Update, context: CallbackContext):
        default_error_message = "It wasn't possible to retrieve the standing"

        last_race = f1_fantasy_service.get_last_completed_race(season=now.year, now=now)
        if isinstance(last_race, Error):
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=default_error_message
            )
        else:
            last_race_standings = f1_fantasy_service.get_last_race_standing(
                race_id=last_race.id
            )
            if isinstance(last_race_standings, Error):
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=default_error_message
                )
            else:
                message = league_standing_to_pretty_table(standing=last_race_standings)
                message.title = last_race.name
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"<pre>{message}</pre>",
                    parse_mode=ParseMode.HTML,
                )

    return get_last_f1_fantasy_race_standing


def get_last_race_team_standing_handler(f1_fantasy_service: F1FantasyService):
    def get_f1_last_race_team_standing_handler(
        update: Update, context: CallbackContext
    ) -> None:
        standings = f1_fantasy_service.get_league_standing()
        inputs = entrant_to_pretty_input(standings)
        update.message.reply_text(
            "Please choose:", reply_markup=InlineKeyboardMarkup(inputs)
        )

    return get_f1_last_race_team_standing_handler


def get_last_race_team_standing_handler_button(
    now: datetime.datetime,
    f1_all_players: dict,
    f1_fantasy_service: F1FantasyService,
):
    def get_f1_last_race_team_standing_handler_button(
        update: Update, context: CallbackContext
    ) -> None:
        query = update.callback_query

        query.answer()
        user_global_id = query.data

        # season parameter hardcoded to current year at the moment
        last_race = f1_fantasy_service.get_last_completed_race(season=now.year, now=now)

        picked_players = f1_fantasy_service.get_last_race_team_standing(
            race_id=last_race.id, user_id=user_global_id, f1_drivers=f1_all_players
        )
        message = picked_players_to_pretty_table(
            picked_players=picked_players, last_race=last_race
        )

        query.edit_message_text(
            text=f"<pre>{message}</pre>",
            parse_mode=ParseMode.HTML,
        )

    return get_f1_last_race_team_standing_handler_button


def get_valid_lineup_reminder_minutes(minutes: List[str]) -> List[float]:
    if not minutes:
        return [30]

    final_minutes = []
    for minute in minutes:
        try:
            m = float(minute)
            if m > 0:
                final_minutes.append(m)
        except (IndexError, ValueError):
            pass
    return final_minutes


def set_lineup_reminders_handler(
    f1_fantasy_service: F1FantasyService, now: datetime.datetime
):
    def set_lineup_reminders(update: Update, context: CallbackContext):

        minutes = get_valid_lineup_reminder_minutes(context.args)

        season_races = f1_fantasy_service.get_season_races(season=now.year)
        next_races = list(filter(lambda r: r.start_timestamp > now, season_races))

        chat_id = update.message.chat_id
        user_id = update.effective_user.id
        job_removed = False

        update.message.reply_text("Setting reminder...")
        for race in next_races:
            job_name = f"{race.id}-{user_id}"
            # Schedule the reminders only if not already present
            for minute in minutes:
                remind_at = race.start_timestamp - datetime.timedelta(
                    minutes=minute
                )
                job_removed = remove_job_if_exists(job_name, context)
                context.job_queue.run_once(
                    callback=send_lineup_reminder,
                    when=remind_at,
                    context=str(chat_id),
                    name=job_name,
                )
        text = f"I will remind you {minutes} before the deadline."
        if job_removed:
            text += "\nOld reminders were removed."
        update.message.reply_text(text)

    return set_lineup_reminders


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    logger.debug("Remove job")
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


# FIXME: find a way to use what is in telegram_command.py to avoid duplication
def get_handlers(
    drivers: dict,
    f1_fantasy_service: F1FantasyService,
) -> List[Handler]:
    return [
        CommandHandler(
            [TELEGRAM_START_COMMAND, TELEGRAM_HELP_COMMAND],
            help_bot_handler(),
        ),
        CommandHandler(
            TELEGRAM_FANTASY_STANDING_COMMAND,
            get_standings_handler(f1_fantasy_service=f1_fantasy_service),
        ),
        CommandHandler(
            TELEGRAM_FANTASY_LAST_GP_STANDING_COMMAND,
            get_last_race_standing_handler(
                now=datetime.datetime.now(),
                f1_fantasy_service=f1_fantasy_service,
            ),
        ),
        CommandHandler(
            TELEGRAM_FANTASY_TEAM_COMMAND,
            get_last_race_team_standing_handler(f1_fantasy_service=f1_fantasy_service),
        ),
        CallbackQueryHandler(
            get_last_race_team_standing_handler_button(
                now=datetime.datetime.now(),
                f1_all_players=drivers,
                f1_fantasy_service=f1_fantasy_service,
            )
        ),
        CommandHandler(
            TELEGRAM_FANTASY_LINEUP_REMINDER,
            set_lineup_reminders_handler(
                now=datetime.datetime.now(),
                f1_fantasy_service=f1_fantasy_service,
            ),
        ),
    ]


def send_lineup_reminder(context: CallbackContext) -> None:
    job = context.job
    context.bot.send_message(
        job.context, text="Hey buddy, it's time to make the lineup for the upcoming GP!"
    )
