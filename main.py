from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()
driver.get("https://account.formula1.com/#/en/login?lead_source=web_fantasy&redirect=https%3A%2F%2Ffantasy.formula1.com%2Fapp%2F%23%2F")
assert "Python" in driver.title
elem = driver.find_element_by_name("q")
elem.clear()
elem.send_keys("pycon")
elem.send_keys(Keys.RETURN)
assert "No results found." not in driver.page_source
driver.close()