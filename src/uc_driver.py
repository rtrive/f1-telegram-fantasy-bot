import logging
from typing import List
from urllib.request import Request

from core.credentials import Credentials
from psutil import Process
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from seleniumwire.undetected_chromedriver import (  # type: ignore
    Chrome as uc_chrome,
    ChromeOptions,
)

logger = logging.getLogger(__name__)


class ChromeDriver:
    def __init__(self, options: ChromeOptions, seleniumwire_options: dict):
        self.driver = uc_chrome(
            options=options, seleniumwire_options=seleniumwire_options, version_main=102
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
        return self.driver.wait_for_request(pat=path, timeout=timeout)

    def get_player_cookie(self) -> str:
        player_cookie = ""
        logger.debug("Get session cookie")
        try:
            self.driver.wait_for_request(
                "/v2/account/subscriber/authenticate/by-password", 120
            )
            request = self.driver.wait_for_request("/f1/2022/sessions", 120)
            player_cookie = request.response.headers.get("Set-Cookie").split(";")[0]
        except TimeoutException as e:
            logger.error(e)
            logger.error("Session timeout - Proceeding to reboot")
            self.reboot()
        return player_cookie

    def reboot(self):
        logger.info("Shutdown for login session")
        Process().terminate()
