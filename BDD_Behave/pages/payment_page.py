import os

from selenium.webdriver.common.by import By

from config.config_reader import ConfigReader
from utils.screenshot_util import ScreenshotUtil
from utils.waits import Waits


class PaymentPage:
    PAYMENT_INDICATOR = (
        By.XPATH,
        "//*[contains(translate(., 'PAYMENT', 'payment'), 'payment') "
        "or contains(translate(., 'PAY NOW', 'pay now'), 'pay now') "
        "or contains(translate(., 'UPI', 'upi'), 'upi') "
        "or contains(translate(., 'CARD', 'card'), 'card') "
        "or contains(translate(., 'NET BANKING', 'net banking'), 'net banking') "
        "or contains(translate(., 'WALLET', 'wallet'), 'wallet')]",
    )

    PASSENGER_ERROR = (
        By.XPATH,
        "//*[contains(.,'Please enter Name') or contains(.,'Please Provide valid Email') "
        "or contains(.,'Please enter Age') or contains(.,'Please select gender')]",
    )

    def __init__(self, driver):
        self.driver = driver
        self.waits = Waits(driver)

    def is_on_payment_page(self):
        if self.waits.is_element_present(*self.PASSENGER_ERROR, timeout=2):
            return False

        current_url = self.driver.current_url.lower()

        if "payment" in current_url or "pay" in current_url:
            return True

        return self.waits.is_element_present(*self.PAYMENT_INDICATOR, timeout=30)

    def capture_payment_page(self):
        screenshots_dir = ConfigReader.get_screenshots_path()
        os.makedirs(screenshots_dir, exist_ok=True)
        return ScreenshotUtil.take_screenshot(self.driver, "payment_page")