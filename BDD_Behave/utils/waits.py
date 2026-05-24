import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config_reader import ConfigReader
from utils.logger import get_logger

logger = get_logger(__name__)


class Waits:
    def __init__(self, driver):
        self.driver = driver
        self.wait_time = ConfigReader.get_explicit_wait()

    def wait_for_element_visible(self, by, locator, timeout=None):
        wait_time = timeout or self.wait_time
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located((by, locator))
            )
        except TimeoutException:
            logger.error(f"Element NOT visible after {wait_time}s: {locator}")
            raise

    def wait_for_element_clickable(self, by, locator, timeout=None):
        wait_time = timeout or self.wait_time
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable((by, locator))
            )
        except TimeoutException:
            logger.error(f"Element NOT clickable after {wait_time}s: {locator}")
            raise

    def wait_for_element_present(self, by, locator, timeout=None):
        wait_time = timeout or self.wait_time
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((by, locator))
            )
        except TimeoutException:
            logger.error(f"Element NOT present after {wait_time}s: {locator}")
            raise

    def wait_for_elements_present(self, by, locator, timeout=None):
        wait_time = timeout or self.wait_time
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_all_elements_located((by, locator))
            )
        except TimeoutException:
            logger.error(f"Elements NOT present after {wait_time}s: {locator}")
            raise

    def wait_for_url_contains(self, text, timeout=None):
        wait_time = timeout or self.wait_time
        try:
            WebDriverWait(self.driver, wait_time).until(EC.url_contains(text))
        except TimeoutException:
            logger.error(f"URL does not contain '{text}' after {wait_time}s")
            raise

    def is_element_present(self, by, locator, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            return True
        except TimeoutException:
            return False

    def is_element_visible(self, by, locator, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, locator))
            )
            return True
        except TimeoutException:
            return False

    def find_first_clickable(self, locators, timeout=10):
        last_error = None
        for by, locator in locators:
            try:
                return self.wait_for_element_clickable(by, locator, timeout=timeout)
            except TimeoutException as error:
                last_error = error
        raise last_error or TimeoutException("No locator became clickable")

    def wait_for_page_ready(self, timeout=None):
        wait_time = timeout or self.wait_time
        WebDriverWait(self.driver, wait_time).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def sleep(self, seconds):
        time.sleep(seconds)

    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)

    def js_click(self, element):
        self.driver.execute_script("arguments[0].click();", element)