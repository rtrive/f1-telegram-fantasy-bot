import os
import sys
import urllib.parse
from time import sleep
from typing import List
from seleniumwire.undetected_chromedriver import Chrome as uc_chrome  # type: ignore
from dotenv import load_dotenv
from telegram_bot import Bot
from credentials import Credentials
from uc_driver import ChromeDriver


F1_FANTASY_LOGIN_URL = "https://account.formula1.com/#/en/login?lead_source=web_fantasy&redirect=https%3A%2F%2Ffantasy.formula1.com%2Fapp%2F%23%2F"  # noqa: E501


def get_player_cookie(driver: uc_chrome) -> str:
    player_cookie = ""
    for resp in driver.requests():
        if resp.url == "https://fantasy-api.formula1.com/f1/2022/sessions?v=1":
            player_cookie = resp.response.headers.get("Set-Cookie").split(";")[0]

    return player_cookie


def manipulate_cookies(cookies: List[dict]) -> str:
    new_cookies = ""
    for cookie in cookies:
        if (
            cookie["name"] == "login"
            or cookie["name"] == "login-session"
            or cookie["name"] == "user-metadata"
        ):
            new_cookies += f'{cookie["name"]}={urllib.parse.quote(cookie["value"])}; '
        else:
            new_cookies += f'{cookie["name"]}={cookie["value"]}; '
    return new_cookies


if __name__ == "__main__":
    load_dotenv()

    driver = ChromeDriver()
    credentials = Credentials(
        username=os.getenv("USERNAME"), password=os.getenv("PASSWORD")
    )
    driver.login(
        url=F1_FANTASY_LOGIN_URL,
        credentials=credentials,
    )

    cookies = driver.get_cookies()
    cookies = manipulate_cookies(cookies=cookies)
    sleep(20)
    driver.close()
    cookies = get_player_cookie(driver)
    print("Ready to be used with bot")
    telegram_bot_api_key = os.getenv("TELEGRAM_BOT_API_KEY")
    if not telegram_bot_api_key:
        sys.exit("Missing telegram api key")
    Bot(telegram_bot_api_key, cookies, F1_FANTASY_LOGIN_URL)
