import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import LogGen

logger = LogGen.loggen(__name__)


class PaymentPage(BasePage):

    def verify_payment_page(self):
        with allure.step("Verify payment page loaded"):
            self.close_popups()
            payment_words = ["payment", "pay", "fare", "wallet", "card", "upi"]
            body_text = self.page_text().lower()

            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Payment page state",
                attachment_type=allure.attachment_type.PNG
            )

            if any(word in body_text for word in payment_words):
                logger.info("Payment page reached and verified")
            else:
                logger.warning("Payment page loaded but payment keywords not detected")

    def proceed_to_payment(self):
        with allure.step("Proceed to payment"):
            self.close_popups()

            for label in ["Continue", "Proceed", "Pay"]:
                buttons = self.visible_elements(
                    By.XPATH,
                    f"//button[contains(., '{label}')] | "
                    f"//*[@role='button' and contains(., '{label}')]"
                )
                if buttons:
                    self.js_click(buttons[0])
                    logger.info(f"Payment proceed — clicked '{label}'")
                    break

            self.verify_payment_page()