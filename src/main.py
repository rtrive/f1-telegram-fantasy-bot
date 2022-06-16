import os
import sys
from logging import Logger

from apscheduler.schedulers.background import BackgroundScheduler

from core.configuration import Configuration, validate_configuration
from dotenv import load_dotenv
from http_server import start as http_server_start
from logger import create_logger
from psutil import Process
from selenium.common.exceptions import TimeoutException
from seleniumwire.undetected_chromedriver import (  # type: ignore
    Chrome as uc_chrome,
    ChromeOptions as uc_chrome_options,
)
from telegram_bot import Bot
from uc_driver import ChromeDriver

LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(filename)s - %(funcName)s: %(message)s"


def reboot(log: Logger):
    log.info("Shutdown for login session")
    Process().terminate()


def get_player_cookie(log: Logger, driver: uc_chrome) -> str:
    player_cookie = ""
    log.debug("get cookie")
    try:
        driver.wait_for_request("/v2/account/subscriber/authenticate/by-password", 120)
        request = driver.wait_for_request("/f1/2022/sessions", 120)
        player_cookie = request.response.headers.get("Set-Cookie").split(";")[0]
        log.debug(player_cookie)
    except TimeoutException as e:
        log.error(e)
        log.error("Session timeout")
        reboot(log)
    return player_cookie


if __name__ == "__main__":
    load_dotenv()

    configuration = Configuration(env_variables=os.environ)
    errors = validate_configuration(configuration)
    log = create_logger(
        name=__name__, level=configuration.log.log_level, format=LOG_FORMAT
    )
    if errors:
        log.error(errors.message)
        sys.exit()
    log.info("Startup")

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=reboot, trigger="interval", hours=24, kwargs={"log": log})
    scheduler.start()

    http_server_start(
        log=create_logger(
            name="http-server", level=configuration.log.log_level, format=LOG_FORMAT
        ),
        hostname=configuration.http_server.hostname,
        port=configuration.http_server.port,
    )

    errors = validate_configuration(configuration)
    if errors:
        log.error(errors.message)
        sys.exit()

    chrome_options = uc_chrome_options()
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    seleniumwire_options = {"connection_keep_alive": True, "disable_encoding": True}
    driver = ChromeDriver(
        options=chrome_options, seleniumwire_options=seleniumwire_options
    )
    driver.login(
        url=configuration.f1_fantasy.login_url,
        credentials=configuration.f1_fantasy.credentials,
    )
    cookies = get_player_cookie(log=log, driver=driver)
    driver.close()
    fantasy_bot = Bot(
        api_key=configuration.bot.api_key,
    )

    log.info("Telegram registering handlers")
    handlers = fantasy_bot.get_handlers(
        cookies=cookies, league_id=configuration.f1_fantasy.league_id
    )
    for handler in handlers:
        fantasy_bot.dispatcher.add_handler(handler=handler)

    log.info("Starting bot")
    fantasy_bot.start_bot()
