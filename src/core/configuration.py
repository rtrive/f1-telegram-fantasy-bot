from collections import UserDict
from typing import List, Optional

from core.credentials import Credentials
from core.error import Error


class BotConfig:
    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key


class F1FantasyConfig:
    def __init__(
        self,
        credentials: Credentials,
        login_url: Optional[str],
        league_id: Optional[str],
    ):
        self.credentials = credentials
        self.login_url = (
            "https://account.formula1.com/#/en/login?lead_source=web_fantasy&redirect=https%3A%2F%2Ffantasy.formula1.com%2Fapp%2F%23%2F"
            if not login_url
            else login_url
        )
        self.league_id = league_id


class Configuration:
    def __init__(self, env_variables: UserDict):
        self.f1_fantasy = F1FantasyConfig(
            credentials=Credentials(
                username=env_variables.get("USERNAME"),
                password=env_variables.get("PASSWORD"),
            ),
            login_url=env_variables.get("F1_FANTASY_LOGIN_URL"),
            league_id=env_variables.get("F1_FANTASY_LEAGUE_ID"),
        )
        self.bot = BotConfig(api_key=env_variables.get("TELEGRAM_BOT_API_KEY"))


def validate_bot_config(errors: List[str], bot_config: BotConfig) -> List[str]:
    if not bot_config.api_key:
        errors.append("Missing Telegram BOT API key")
    return errors


def validate_credentials(errors: List[str], credentials: Credentials) -> List[str]:
    if not credentials.username:
        errors.append("F1 Fantasy username is missing")
    if not credentials.password:
        errors.append("F1 Fantasy password is missing")

    return errors


def validate_f1_fantasy_config(
    errors: List[str], f1_fantasy_config: F1FantasyConfig
) -> List[str]:
    if not f1_fantasy_config.league_id:
        errors.append("F1 Fantasy league id is missing")
    return validate_credentials(errors, f1_fantasy_config.credentials)


def validate_configuration(config: Configuration) -> Error:
    errors = validate_f1_fantasy_config([], config.f1_fantasy)
    errors = validate_bot_config(errors, config.bot)
    if errors:
        error_message = "\n".join(map(str, errors))
        return Error(error_message)
    else:
        return None
