import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.logger import LogGen

logger = LogGen.loggen(__name__)


class LoginPage(BasePage):

    def login_with_phone(self, mobile):
        with allure.step("Login with phone number"):
            self.close_popups()

            self.click_first_visible(
                By.XPATH,
                "//button[contains(., 'Log in') or contains(., 'Login') or "
                "contains(., 'Sign up') or contains(., 'SignUp')]"
            )
            logger.info("Login button clicked")

            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Login modal opened",
                attachment_type=allure.attachment_type.PNG
            )

            self.close_popups()

            mobile_input = self.first_visible(
                By.XPATH,
                "//input[contains(@placeholder, 'Mobile') or "
                "contains(@placeholder, 'mobile')]"
            )
            mobile_input.clear()
            mobile_input.send_keys(str(mobile))
            logger.info("Mobile number entered")

            continue_button = self.first_visible(
                By.XPATH, "//button[contains(., 'Continue')]"
            )
            self.js_click(continue_button)
            logger.info("Continue clicked — waiting for OTP")

            self.wait_for_manual_otp()

            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Post-login state",
                attachment_type=allure.attachment_type.PNG
            )

    def wait_for_manual_otp(self):
        logger.info("Waiting up to 120 seconds for manual OTP completion...")
        try:
            WebDriverWait(self.driver, 120).until(
                lambda driver: "log in to ixigo" not in self.page_text().lower()
                and "enter mobile number" not in self.page_text().lower()
            )
            logger.info("OTP completed successfully")
        except TimeoutException:
            logger.warning("OTP wait timed out — continuing anyway")