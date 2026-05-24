import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config.config_reader import ConfigReader
from utils.logger import get_logger
from utils.screenshot_util import ScreenshotUtil
from utils.waits import Waits

logger = get_logger(__name__)


class LoginPage:
    MOBILE_INPUT = (By.XPATH, "//input[@placeholder='Mobile no.' or @placeholder='Enter Mobile Number' or @type='tel']")
    CONTINUE_BTN = (By.XPATH, "//button[normalize-space()='CONTINUE' or normalize-space()='Continue' or normalize-space()='continue']")
    LOGIN_MODAL = (By.XPATH, "//input[@placeholder='Mobile no.' or @placeholder='Enter Mobile Number'] | //*[contains(@class,'abrs-modal')]")
    LOGGED_IN_HEADER = (By.XPATH, "//*[contains(.,'My Trips') or contains(.,'Logout') or contains(.,'Hi,')]")

    def __init__(self, driver):
        self.driver = driver
        self.waits = Waits(driver)

    def enter_mobile_number(self, mobile):
        logger.info("Entering mobile number")
        mobile_input = self.waits.wait_for_element_visible(*self.MOBILE_INPUT, timeout=15)
        mobile_input.clear()
        mobile_input.send_keys(str(mobile))
        time.sleep(1)
        ScreenshotUtil.take_screenshot(self.driver, "login_mobile_entered")

    def click_continue(self):
        logger.info("Clicking login Continue")
        continue_button = self.waits.wait_for_element_clickable(*self.CONTINUE_BTN, timeout=15)
        self.waits.js_click(continue_button)
        time.sleep(2)
        ScreenshotUtil.take_screenshot(self.driver, "login_continue_clicked")

    def wait_for_manual_otp(self):
        timeout = ConfigReader.get_manual_otp_timeout()
        logger.info("Waiting for manual OTP entry")
        print(f"\nEnter the OTP manually in the Chrome window. Automation will wait up to {timeout} seconds.\n")

        try:
            WebDriverWait(self.driver, timeout).until(lambda driver: self.is_login_completed())
        except TimeoutException:
            ScreenshotUtil.take_screenshot(self.driver, "manual_otp_timeout")
            raise AssertionError("Manual OTP was not completed before timeout.")

        ScreenshotUtil.take_screenshot(self.driver, "login_completed")

    def is_login_completed(self):
        current_url = self.driver.current_url.lower()
        modal_visible = self.waits.is_element_visible(*self.LOGIN_MODAL, timeout=1)
        logged_indicator = self.waits.is_element_present(*self.LOGGED_IN_HEADER, timeout=1)
        return logged_indicator or (not modal_visible and "login" not in current_url)