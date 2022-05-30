import os
import sys
import json
from time import sleep
from typing import Any, List
from seleniumwire.undetected_chromedriver import Chrome as uc_chrome  # type: ignore
from undetected_chromedriver import ChromeOptions as uc_chrome_options  # type: ignore
from seleniumwire.utils import decode
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from telegram_bot import Bot


F1_FANTASY_DRIVER_URL = "https://account.formula1.com/#/en/login?lead_source=web_fantasy&redirect=https%3A%2F%2Ffantasy.formula1.com%2Fapp%2F%23%2F"  # noqa: E501


def manipulate_cookies(cookies: List[dict]) -> dict:
    new_cookies = {}
    for cookie in cookies:
        new_cookies[cookie["name"]] = cookie["value"]
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
    cookies = driver.get_cookies()

    sleep(20)

    for resp in driver.requests:
        if (
            resp.url
            == "https://api.formula1.com/v2/account/subscriber/authenticate/by-password"
        ):
            body = json.loads(
                decode(
                    resp.response.body,
                    resp.response.headers.get("Content-Encoding", "identity"),
                )
            )
    driver.close()
    cookies = manipulate_cookies(cookies)
    cookies["login-session"] = json.dumps({"data": body["data"]})
    print("Ready to be used with bot")
    telegram_bot_api_key = os.getenv("TELEGRAM_BOT_API_KEY")
    if not password:
        sys.exit("Missing telegram api key")
    Bot(telegram_bot_api_key, cookies, F1_FANTASY_DRIVER_URL)
