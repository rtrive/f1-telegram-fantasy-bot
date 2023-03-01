import os
import sys

import requests  # type: ignore

from apscheduler.schedulers.background import BackgroundScheduler

from bot.handlers import get_handlers
from bot.telegram_bot import Bot

from core.configuration import Configuration, validate_configuration
from dotenv import load_dotenv

from http_client import HTTPClient
from http_server import start as http_server_start
from logger import create_logger
from seleniumwire.undetected_chromedriver import (  # type: ignore
    ChromeOptions as uc_chrome_options,
)

from services.f1_fantasy_service import F1FantasyService
from uc_driver import ChromeDriver

LOG_FORMAT = "[%(levelname)s] %(asctime)s - %(filename)s - %(funcName)s: %(message)s"


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

    log.info("Starting HTTP server")
    http_server_start(
        log=create_logger(
            name="http-server", level=configuration.log.log_level, format=LOG_FORMAT
        ),
        hostname=configuration.http_server.hostname,
        port=configuration.http_server.port,
    )

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

    log.info("Scheduling restart")
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=driver.reboot, trigger="interval", hours=24)
    scheduler.start()

    log.info("Performing login")
    driver.login(
        url=configuration.f1_fantasy.login_url,
        credentials=configuration.f1_fantasy.credentials,
    )
    cookies = driver.get_player_cookie()
    driver.close()

    fantasy_bot = Bot(
        api_key=configuration.bot.api_key, db_config=configuration.db_config
    )

    log.info("Loading drivers")

    f1_drivers_req = requests.get(
        url="https://fantasy.formula1.com/feeds/drivers/1_en.json?buster=20230227110410",
        cookies={"Cookie": cookies}
    )

    f1_drivers = f1_drivers_req.json()["Data"]["Value"]
    f1_all_drivers = {}
    for f1_driver in f1_drivers:
        if f1_driver["PositionName"] == "DRIVER":
            f1_all_drivers[int(f1_driver["PlayerId"])] = f1_driver["FUllName"].split(" ")[1]

    log.info("Creating F1 Fantasy base HTTP client")
    f1_fantasy_http_client = HTTPClient(
        base_url="https://fantasy.formula1.com",
    )
    log.info("Creating Season Service")
    f1_fantasy_service = F1FantasyService(
        http_client=f1_fantasy_http_client,
        logger=create_logger(
            "f1-fantasy-service", level=configuration.log.log_level, format=LOG_FORMAT
        ),
        cookies=cookies,
        league_id=configuration.f1_fantasy.league_id,
    )

    log.info("Telegram registering handlers")
    handlers = get_handlers(
        drivers=f1_all_drivers,
        f1_fantasy_service=f1_fantasy_service,
    )
    for handler in handlers:
        fantasy_bot.dispatcher.add_handler(handler=handler)

    log.info("Starting bot")
    fantasy_bot.start_bot()
