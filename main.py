import os
import sys
from typing import List
from uc_driver import ChromeDriver
from dotenv import load_dotenv


def manipulate_cookies(cookies: List[dict]) -> dict:
    new_cookies = {}
    for cookie in cookies:
        new_cookies[cookie["name"]] = cookie["value"]
    return new_cookies


if __name__ == "__main__":
    load_dotenv()
    username = os.getenv("USERNAME")
    if not username:
        sys.exit("Missing username")
    password = os.getenv("PASSWORD")
    if not password:
        sys.exit("Missing password")

    driver = ChromeDriver()
    driver.login(
        url="https://account.formula1.com/#/en/login?lead_source=web_fantasy&redirect=https%3A%2F%2Ffantasy.formula1.com%2Fapp%2F%23%2F",  # noqa: E501
        username=username,
        password=password,
    )

    cookies = driver.get_cookies()
    cookies = manipulate_cookies(cookies=cookies)
    driver.close()
