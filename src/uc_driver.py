from urllib.request import Request
from seleniumwire.undetected_chromedriver import Chrome as uc_chrome  # type: ignore
from seleniumwire.undetected_chromedriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from typing import List
from credentials import Credentials


class ChromeDriver:
    def __init__(self, options: ChromeOptions, seleniumwire_options: dict):
        self.driver = uc_chrome(
            options=options, seleniumwire_options=seleniumwire_options
        )

    def go_to_page(self, url: str) -> None:
        self.driver.get(url=url)

    def click_button_by_id(self, by_type: str, button_id: str) -> None:
        self.driver.find_element(by=by_type, value=button_id).click()

    def fill_text_area(self, by_type: str, element_value: str, value) -> None:
        self.elem = self.driver.find_element(by=by_type, value=element_value)
        self.elem.clear()
        self.elem.send_keys(value)

    def send_key(self, key: Keys) -> None:
        self.elem.send_keys(key)

    def get_cookies(self) -> List[dict]:
        return self.driver.get_cookies()

    def close(self) -> None:
        self.driver.close()

    def login(self, url: str, credentials: Credentials) -> None:
        self.go_to_page(url=url)
        self.click_button_by_id(by_type=By.ID, button_id="truste-consent-button")
        self.fill_text_area(
            by_type=By.NAME, element_value="Login", value=credentials.username
        )
        self.fill_text_area(
            by_type=By.NAME, element_value="Password", value=credentials.password
        )
        self.send_key(key=Keys.RETURN)

    def requests(self) -> List[Request]:
        return self.driver.requests

    def wait_for_request(self, path: str, timeout: int):
        print("wait for request")
        return self.driver.wait_for_request(pat=path, timeout=timeout)
