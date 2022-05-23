import os
import sys
from typing import List
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def manipulate_cookies(cookies: List[dict]) -> dict:
    new_cookies = {}
    for cookie in cookies:
        new_cookies[cookie["name"]] = cookie["value"]
    return new_cookies

def create_diver():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    return driver


def go_to_page(driver, url):
    driver.get(url)


def click_button_by_id(driver, by_type, button_id):
    driver.find_element(by=by_type, value=button_id).click()


def fill_text_area(driver, by_type, element_value, value):
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
    go_to_page(driver, "https://account.formula1.com/#/en/login?lead_source=web_fantasy&redirect=https%3A%2F%2Ffantasy.formula1.com%2Fapp%2F%23%2F")
    click_button_by_id(driver, By.ID, "truste-consent-button")

    fill_text_area(driver, By.NAME, "Login", username)

    elem = fill_text_area(driver, By.NAME, "Password", password)
    elem.send_keys(Keys.RETURN)
    cookies = driver.get_cookies()
    cookies = manipulate_cookies(cookies)
    driver.close()
