import os
import sys
from typing import Any, Literal
from undetected_chromedriver import Chrome as uc_chrome
from undetected_chromedriver import ChromeOptions as uc_chrome_options
from time import sleep
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def create_diver() -> uc_chrome:
    options = uc_chrome_options()
    driver = uc_chrome(options=options)
    return driver


def go_to_page(driver: uc_chrome, url: str) -> None:
    driver.get(url)


def click_button_by_id(driver: uc_chrome, by_type: Literal, button_id: str) -> None:
    driver.find_element(by=by_type, value=button_id).click()


def fill_text_area(
    driver: uc_chrome, by_type: Literal, element_value: str, value
) -> Any:
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
        "https://account.formula1.com/#/en/login?lead_source=web_fantasy&redirect=https%3A%2F%2Ffantasy.formula1.com%2Fapp%2F%23%2F",  # noqa: E501
    )
    click_button_by_id(driver, By.ID, "truste-consent-button")

    fill_text_area(driver, By.NAME, "Login", username)

    elem = fill_text_area(driver, By.NAME, "Password", password)
    elem.send_keys(Keys.RETURN)
    sleep(30)
    driver.close()
