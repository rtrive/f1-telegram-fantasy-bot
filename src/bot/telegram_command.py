TELEGRAM_HELP_COMMAND = "help"
TELEGRAM_START_COMMAND = "start"
TELEGRAM_FANTASY_LAST_GP_STANDING_COMMAND = "last_gp_standing"
TELEGRAM_FANTASY_STANDING_COMMAND = "standing"


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
]
