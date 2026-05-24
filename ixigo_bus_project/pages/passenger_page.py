import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from pages.base_page import BasePage
from utils.logger import LogGen

logger = LogGen.loggen(__name__)


class PassengerPage(BasePage):

    def fill_passenger_details(self, name, age, gender, mobile):
        with allure.step("Fill passenger details"):
            self.close_popups()

            self._type_if_present(
                "//input[contains(@placeholder, 'Name') or contains(@name, 'name')]",
                name
            )
            self._type_if_present(
                "//input[contains(@placeholder, 'Age') or contains(@name, 'age')]",
                age
            )
            self._type_if_present(
                "//input[contains(@placeholder, 'Mobile') or contains(@name, 'mobile')]",
                mobile
            )
            self._select_gender(gender)

            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Passenger form filled",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"Passenger details filled — name={name}, age={age}, gender={gender}")

    def continue_to_payment(self):
        with allure.step("Continue to payment"):
            for label in ["Continue", "Proceed", "Pay"]:
                buttons = self.visible_elements(
                    By.XPATH,
                    f"//button[contains(., '{label}')] | "
                    f"//*[@role='button' and contains(., '{label}')]"
                )
                if buttons:
                    self.js_click(buttons[0])
                    allure.attach(
                        self.driver.get_screenshot_as_png(),
                        name=f"Clicked '{label}' to payment",
                        attachment_type=allure.attachment_type.PNG
                    )
                    logger.info(f"Continue to payment — clicked '{label}'")
                    return

            logger.warning("Passenger continue button not found")

    def _type_if_present(self, xpath, value):
        if value in (None, ""):
            return
        try:
            field = self.first_visible(By.XPATH, xpath)
            field.clear()
            field.send_keys(str(value))
        except TimeoutException:
            pass

    def _select_gender(self, gender):
        if not gender:
            return
        gender_text = str(gender).strip()
        try:
            option = self.first_visible(
                By.XPATH, f"//*[normalize-space()='{gender_text}']"
            )
            self.js_click(option)
            return
        except TimeoutException:
            pass
        try:
            select_element = self.first_visible(By.TAG_NAME, "select")
            Select(select_element).select_by_visible_text(gender_text)
        except Exception:
            pass