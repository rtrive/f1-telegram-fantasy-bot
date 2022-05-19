from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36')
driver = webdriver.Chrome(options=options)
driver.get("https://account.formula1.com/#/en/login")
cookie_accept = driver.find_element_by_id("truste-consent-button").click()
elem = driver.find_element_by_name("Login")
elem = driver.find_element(by=By.NAME, value="Login")
elem.clear()
elem.send_keys("")
elem = driver.find_element(by=By.NAME, value="Password")
elem.clear()
elem.send_keys("")
elem.send_keys(Keys.RETURN)
sleep(10)
driver.get_screenshot_as_file("./test.png")
driver.close()
