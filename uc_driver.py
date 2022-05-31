from undetected_chromedriver import Chrome as uc_chrome  # type: ignore
from undetected_chromedriver import ChromeOptions as uc_chrome_options  # type: ignore
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from typing import List


class ChromeDriver:
    def __init__(self):
        self.options = uc_chrome_options()
        self.options.add_argument("--headless")
        self.driver = uc_chrome(options=self.options)

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

    def login(self, url: str, username: str, password: str) -> None:
        self.go_to_page(url=url)
        self.click_button_by_id(by_type=By.ID, button_id="truste-consent-button")
        self.fill_text_area(by_type=By.NAME, element_value="Login", value=username)
        self.fill_text_area(by_type=By.NAME, element_value="Password", value=password)
        self.send_key(key=Keys.RETURN)
