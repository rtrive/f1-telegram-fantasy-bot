import os
import sys
from time import sleep
from seleniumwire.undetected_chromedriver import Chrome as uc_chrome  # type: ignore
from seleniumwire.undetected_chromedriver import (
    ChromeOptions as uc_chrome_options,
)
from dotenv import load_dotenv
from telegram.ext import CommandHandler, MessageHandler, filters

from telegram_bot import Bot
from credentials import Credentials
from uc_driver import ChromeDriver

F1_FANTASY_LOGIN_URL = "https://account.formula1.com/#/en/login?lead_source=web_fantasy&redirect=https%3A%2F%2Ffantasy.formula1.com%2Fapp%2F%23%2F"  # noqa: E501


def get_player_cookie(driver: uc_chrome) -> str:
    sleep_count = 0
    player_cookie = ""
    while sleep_count <= 7:
        for resp in driver.requests():
            if resp.url == "https://fantasy-api.formula1.com/f1/2022/sessions?v=1":
                player_cookie = resp.response.headers.get("Set-Cookie").split(";")[0]
                print(player_cookie)
                return player_cookie
        sleep(5)
        sleep_count += 1
    print("Error session")
    return player_cookie


if __name__ == "__main__":
    load_dotenv()

    chrome_options = uc_chrome_options()
    # chrome_options.add_argument("--headless")
    seleniumwire_options = {"connection-keep-alive": True, "disable-encoding": True}
    driver = ChromeDriver(
        options=chrome_options, seleniumwire_options=seleniumwire_options
    )
    credentials = Credentials(
        username=os.getenv("USERNAME"), password=os.getenv("PASSWORD")
    )
    driver.login(
        url=F1_FANTASY_LOGIN_URL,
        credentials=credentials,
    )

    cookies = get_player_cookie(driver)
    driver.close()
    telegram_bot_api_key = os.getenv("TELEGRAM_BOT_API_KEY")
    if not telegram_bot_api_key:
        sys.exit("Missing telegram api key")
    fantasy_bot = Bot(api_key=telegram_bot_api_key)
    league_id = os.getenv("F1_FANTASY_LEAGUE_ID")
    if not league_id:
        sys.exit("Missing league id")

    print("Registering handlers")
    fantasy_bot.application.add_handler(
        CommandHandler("start", Bot.start_bot_handler())
    )
    fantasy_bot.application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), Bot.echo_handler())
    )
    fantasy_bot.application.add_handler(
        CommandHandler(
            "standings", Bot.get_standings(cookies=cookies, league_id=league_id)
        )
    )

    print("Starting bot")
    fantasy_bot.start_bot()
