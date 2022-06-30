TELEGRAM_HELP_COMMAND = "help"
TELEGRAM_START_COMMAND = "start"
TELEGRAM_FANTASY_LAST_GP_STANDING_COMMAND = "last_gp_standing"
TELEGRAM_FANTASY_STANDING_COMMAND = "standing"
TELEGRAM_FANTASY_TEAM_COMMAND = "last_gp_team_result"
TELEGRAM_FANTASY_LINEUP_REMINDER = "lineup_reminder"


class TelegramCommand:
    def __init__(self, name: str, description: str, active: bool = True):
        self.name = name
        self.description = description
        self.active = active


COMMANDS = [
    TelegramCommand(
        name=TELEGRAM_START_COMMAND, description="Start the Bot", active=False
    ),
    TelegramCommand(
        name=TELEGRAM_HELP_COMMAND,
        description=f"You don't know how to use me? Just type /{TELEGRAM_HELP_COMMAND}",
    ),
    TelegramCommand(
        name=TELEGRAM_FANTASY_LAST_GP_STANDING_COMMAND,
        description="Get F1 Fantasy standing of last GP",
    ),
    TelegramCommand(
        name=TELEGRAM_FANTASY_STANDING_COMMAND,
        description="Get F1 Fantasy league standing",
    ),
    TelegramCommand(
        name=TELEGRAM_FANTASY_TEAM_COMMAND,
        description="Get F1 Fantasy league standing for single team",
    ),
    TelegramCommand(
        name=TELEGRAM_FANTASY_LINEUP_REMINDER,
        description=f"Remind me to make the lineup. You can set the minutes "
        f"before the starting date to be reminded."
        f"\n/{TELEGRAM_FANTASY_LINEUP_REMINDER} <minutes>\n"
        f"Example: /{TELEGRAM_FANTASY_LINEUP_REMINDER} 10\n"
        f"Example: /{TELEGRAM_FANTASY_LINEUP_REMINDER} 10 30\n"
        f"If no parameters are provided, the default value is 30 minutes.\n"
        f"If an invalid value is provided, it will be ignored.",
    ),
]
