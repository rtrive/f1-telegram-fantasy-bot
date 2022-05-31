import os
import sys
import urllib.parse
from time import sleep
from typing import Any, List
from seleniumwire.undetected_chromedriver import Chrome as uc_chrome  # type: ignore
from undetected_chromedriver import ChromeOptions as uc_chrome_options  # type: ignore
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from telegram_bot import Bot


F1_FANTASY_DRIVER_URL = "https://account.formula1.com/#/en/login?lead_source=web_fantasy&redirect=https%3A%2F%2Ffantasy.formula1.com%2Fapp%2F%23%2F"  # noqa: E501


def get_player_cookie(driver: uc_chrome) -> str:

    for resp in driver.requests:
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


def create_diver() -> uc_chrome:
    options = uc_chrome_options()
    options.add_argument("--headless")
    driver = uc_chrome(options=options)
    return driver


def go_to_page(driver: uc_chrome, url: str) -> None:
    driver.get(url)


def click_button_by_id(driver: uc_chrome, by_type: str, button_id: str) -> None:
    driver.find_element(by=by_type, value=button_id).click()


def fill_text_area(driver: uc_chrome, by_type: str, element_value: str, value) -> Any:
    elem = driver.find_element(by=by_type, value=element_value)
    elem.clear()
    elem.send_keys(value)
    return elem


if __name__ == "__main__":
    load_dotenv()
    username = os.getenv("USERNAME")
    if not username:
        sys.exit("Missing username")
    password = os.getenv("PASSWORD")
    if not password:
        sys.exit("Missing password")
    driver = create_diver()
    go_to_page(
        driver,
        F1_FANTASY_DRIVER_URL,
    )
    click_button_by_id(driver, By.ID, "truste-consent-button")

    fill_text_area(driver, By.NAME, "Login", username)

    elem = fill_text_area(driver, By.NAME, "Password", password)
    elem.send_keys(Keys.RETURN)
    cookies = driver.get_cookies()
    sleep(30)
    driver.close()
    cookies = get_player_cookie(driver)
    print("Ready to be used with bot")
    telegram_bot_api_key = os.getenv("TELEGRAM_BOT_API_KEY")
    if not telegram_bot_api_key:
        sys.exit("Missing telegram api key")
    Bot(telegram_bot_api_key, cookies, F1_FANTASY_DRIVER_URL)
