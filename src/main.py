import datetime
import os
import sys
import logging
from psutil import Process
from apscheduler.schedulers.background import BackgroundScheduler
from seleniumwire.undetected_chromedriver import Chrome as uc_chrome  # type: ignore
from seleniumwire.undetected_chromedriver import (
    ChromeOptions as uc_chrome_options,
)
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from telegram.ext import CommandHandler, MessageHandler, filters

from telegram_bot import Bot
from core.configuration import Configuration, validate_configuration
from uc_driver import ChromeDriver

LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(filename)s - %(funcName)s: %(message)s"
# Fix: doesn't work since it outside loadenv() scope
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(level=LOG_LEVEL)


def reboot():
    print("Shutdown for login session")
    Process().terminate()


def get_player_cookie(driver: uc_chrome) -> str:
    player_cookie = ""
    logger.info("get cookie")
    try:
        request = driver.wait_for_request("/f1/2022/sessions", 60)
        player_cookie = request.response.headers.get("Set-Cookie").split(";")[0]
        logger.info(player_cookie)
    except TimeoutException as e:
        logger.error(e)
        logger.error("Session timeout")
    return player_cookie


if __name__ == "__main__":
    logger.info("Startup")

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=reboot, trigger="interval", hours=24)
    scheduler.start()

    load_dotenv()
    configuration = Configuration(env_variables=os.environ)
    errors = validate_configuration(configuration)
    if errors:
        logger.error(errors.message)
        sys.exit()

    chrome_options = uc_chrome_options()
    chrome_options.add_argument("--headless")
    seleniumwire_options = {"connection-keep-alive": True, "disable-encoding": True}
    driver = ChromeDriver(
        options=chrome_options, seleniumwire_options=seleniumwire_options
    )
    driver.login(
        url=configuration.f1_fantasy.login_url,
        credentials=configuration.f1_fantasy.credentials,
    )
    cookies = get_player_cookie(driver)
    driver.close()
    fantasy_bot = Bot(api_key=configuration.bot.api_key)
    league_id = configuration.f1_fantasy.league_id

    logging.info("Telegram registering handlers")
    fantasy_bot.application.add_handler(
        CommandHandler("start", Bot.start_bot_handler())
    )
    fantasy_bot.application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), Bot.echo_handler())
    )
    fantasy_bot.application.add_handler(
        CommandHandler(
            "standings", fantasy_bot.get_standings(cookies=cookies, league_id=league_id)
        )
    )

    fantasy_bot.application.add_handler(
        CommandHandler(
            "last_gp_standings",
            fantasy_bot.get_last_race_standing(
                cookies=cookies, league_id=league_id, now=datetime.datetime.now()
            ),
        )
    )

    logging.info("Starting bot")
    fantasy_bot.start_bot()
