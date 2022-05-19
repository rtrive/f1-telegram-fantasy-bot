import os
import sys
from time import sleep
from dotenv import load_dotenv

from selenium import webdriver

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def create_diver():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--disable-extensions")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
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
    go_to_page(driver, "https://account.formula1.com/#/en/login")
    click_button_by_id(driver, By.ID, "truste-consent-button")

    fill_text_area(driver, By.NAME, "Login", username)

    elem = fill_text_area(driver, By.NAME, "Password", password)
    elem.send_keys(Keys.RETURN)
    sleep(30)
    driver.close()
