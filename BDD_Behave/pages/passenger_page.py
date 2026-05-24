import time

from selenium.webdriver.common.by import By

from utils.logger import get_logger
from utils.screenshot_util import ScreenshotUtil
from utils.waits import Waits

logger = get_logger(__name__)


class PassengerPage:
    PROCEED_BTN = (
        By.XPATH,
        "//button[contains(.,'Continue to Pay') or contains(.,'Proceed') or contains(.,'Continue') "
        "or contains(.,'Payment') or contains(.,'Pay')] | "
        "//a[contains(.,'Continue to Pay') or contains(.,'Proceed') or contains(.,'Continue') "
        "or contains(.,'Payment') or contains(.,'Pay')]",
    )

    def __init__(self, driver):
        self.driver = driver
        self.waits = Waits(driver)

    def fill_passenger_details(self, passenger_data: dict):
        passenger_data = {str(k).lower(): v for k, v in passenger_data.items() if v is not None}
        logger.info("Filling passenger details: %s", passenger_data)

        name = str(passenger_data.get("name", "Pramithi Pal"))
        age = str(int(passenger_data.get("age", 23)))
        gender = str(passenger_data.get("gender", "Female"))
        email = str(passenger_data.get("email", "pramithi03.pal@gmail.com"))
        phone = str(passenger_data.get("phone") or passenger_data.get("mobile") or "9875608676")

        self.waits.wait_for_page_ready(timeout=20)
        time.sleep(2)

        self._set_input_value(["Name"], name, "Name")
        self._set_input_value(["Age"], age, "Age")
        self._select_gender(gender)
        self._set_input_value(["Email ID", "Email", "email"], email, "Email")
        self._set_input_value(["Mobile Number", "Mobile", "Phone", "Contact"], phone, "Phone")

        self._select_free_cancellation_option()

        time.sleep(2)
        ScreenshotUtil.take_screenshot(self.driver, "passenger_details_filled")

    def _set_input_value(self, placeholders, value, field_name):
        logger.info("Setting %s: %s", field_name, value)

        success = self.driver.execute_script(
            """
            const labels = arguments[0].map(v => String(v).toLowerCase());
            const value = String(arguments[1]);

            const isVisible = (element) => {
              const rect = element.getBoundingClientRect();
              const style = window.getComputedStyle(element);
              return rect.width > 0
                && rect.height > 0
                && style.display !== 'none'
                && style.visibility !== 'hidden';
            };

            const matches = [...document.querySelectorAll('input, textarea')]
              .filter(element => {
                const placeholder = (element.getAttribute('placeholder') || '').toLowerCase();
                const name = (element.getAttribute('name') || '').toLowerCase();
                const id = (element.getAttribute('id') || '').toLowerCase();
                const type = (element.getAttribute('type') || '').toLowerCase();
                const haystack = `${placeholder} ${name} ${id} ${type}`;
                return labels.some(label => haystack.includes(label));
              })
              .filter(isVisible);

            const element = matches[0];
            if (!element) {
              return false;
            }

            element.scrollIntoView({block: 'center'});
            element.focus();

            const prototype = element.tagName.toLowerCase() === 'textarea'
              ? window.HTMLTextAreaElement.prototype
              : window.HTMLInputElement.prototype;

            const valueSetter = Object.getOwnPropertyDescriptor(prototype, 'value').set;

            valueSetter.call(element, '');
            element.dispatchEvent(new Event('input', {bubbles: true}));
            element.dispatchEvent(new Event('change', {bubbles: true}));

            valueSetter.call(element, value);
            element.dispatchEvent(new Event('input', {bubbles: true}));
            element.dispatchEvent(new Event('change', {bubbles: true}));
            element.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true}));
            element.blur();

            return element.value === value;
            """,
            placeholders,
            value,
        )

        if not success:
            logger.warning("%s field was not set", field_name)

        time.sleep(1)

    def _select_gender(self, gender):
        gender_text = "Female"

        if gender.lower() in ("male", "m"):
            gender_text = "Male"

        logger.info("Selecting gender: %s", gender_text)

        success = self.driver.execute_script(
            """
            const wanted = String(arguments[0]).toLowerCase();

            const isVisible = (element) => {
              const rect = element.getBoundingClientRect();
              const style = window.getComputedStyle(element);
              return rect.width > 0
                && rect.height > 0
                && style.display !== 'none'
                && style.visibility !== 'hidden';
            };

            const candidates = [...document.querySelectorAll('button, div, span, label')]
              .filter(element => (element.innerText || '').trim().toLowerCase() === wanted)
              .filter(isVisible);

            const element = candidates[0];

            if (!element) {
              return false;
            }

            element.scrollIntoView({block: 'center'});
            element.click();

            element.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
            element.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
            element.dispatchEvent(new MouseEvent('click', {bubbles: true}));

            if (element.parentElement) {
              element.parentElement.click();
            }

            return true;
            """,
            gender_text,
        )

        if not success:
            logger.warning("Gender option was not selected: %s", gender_text)

        time.sleep(1)

    def click_proceed_to_payment(self):
        logger.info("Clicking Proceed to Payment")

        clicked = False
        for attempt in range(2):
            time.sleep(2)
            self._select_free_cancellation_option()
            self._scroll_to_continue_button_area()

            clicked = self._click_continue_to_pay_button()
            time.sleep(5)

            if not self._has_free_cancellation_error():
                break

            logger.info("Free cancellation validation still visible. Retrying option selection.")

        if not clicked:
            ScreenshotUtil.take_screenshot(self.driver, "proceed_to_payment_not_found")
            raise Exception("Proceed to Payment button not found or disabled")

        time.sleep(8)
        ScreenshotUtil.take_screenshot(self.driver, "proceed_to_payment_clicked")

    def _select_free_cancellation_option(self):
        logger.info("Selecting free cancellation preference")

        clicked = self.driver.execute_script(
            """
            const wantedText = "no, i don't want this";

            const isVisible = (element) => {
              const rect = element.getBoundingClientRect();
              const style = window.getComputedStyle(element);
              return rect.width > 0
                && rect.height > 0
                && style.display !== 'none'
                && style.visibility !== 'hidden';
            };

            const textNodes = [...document.querySelectorAll('div, label, span, p')]
              .filter(element => (element.innerText || '').trim().toLowerCase().includes(wantedText))
              .filter(isVisible)
              .sort((a, b) => {
                const ar = a.getBoundingClientRect();
                const br = b.getBoundingClientRect();
                return (ar.width * ar.height) - (br.width * br.height);
              });

            const textElement = textNodes[0];
            if (!textElement) {
              return false;
            }

            let card = textElement;
            for (let i = 0; i < 8 && card.parentElement; i++) {
              const rect = card.getBoundingClientRect();
              const text = (card.innerText || '').toLowerCase();
              if (text.includes(wantedText) && rect.width > 300 && rect.height > 40) {
                break;
              }
              card = card.parentElement;
            }

            card.scrollIntoView({block: 'center'});
            window.scrollBy(0, -120);

            const radio = card.querySelector('input[type="radio"], [role="radio"]');
            if (radio) {
              radio.click();
              radio.dispatchEvent(new MouseEvent('click', {bubbles: true}));
              return true;
            }

            const rect = card.getBoundingClientRect();
            const x = rect.left + 35;
            const y = rect.top + rect.height / 2;
            const target = document.elementFromPoint(x, y) || card;

            target.dispatchEvent(new MouseEvent('mousemove', {bubbles: true, clientX: x, clientY: y}));
            target.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, clientX: x, clientY: y}));
            target.dispatchEvent(new MouseEvent('mouseup', {bubbles: true, clientX: x, clientY: y}));
            target.dispatchEvent(new MouseEvent('click', {bubbles: true, clientX: x, clientY: y}));

            card.click();
            card.dispatchEvent(new MouseEvent('click', {bubbles: true}));

            return true;
            """
        )

        if clicked:
            logger.info("Free cancellation preference selected")
            time.sleep(1)
        else:
            logger.info("Free cancellation preference not visible yet")

    def _scroll_to_continue_button_area(self):
        self.driver.execute_script(
            """
            const buttons = [...document.querySelectorAll('button, a, div[role="button"]')]
              .filter(element => /continue to pay/i.test(element.innerText || ''));

            if (buttons.length) {
              buttons[0].scrollIntoView({block: 'center'});
            } else {
              window.scrollTo(0, document.body.scrollHeight);
            }
            """
        )
        time.sleep(1)

    def _click_continue_to_pay_button(self):
        return self.driver.execute_script(
            """
            const words = ['continue to pay', 'proceed to payment', 'proceed', 'continue', 'payment', 'pay'];

            const isVisible = (element) => {
              const rect = element.getBoundingClientRect();
              const style = window.getComputedStyle(element);
              return rect.width > 0
                && rect.height > 0
                && style.display !== 'none'
                && style.visibility !== 'hidden';
            };

            const candidates = [...document.querySelectorAll('button, a, div[role="button"]')]
              .filter(element => {
                const text = (element.innerText || '').trim().toLowerCase();
                return words.some(word => text.includes(word));
              })
              .filter(isVisible)
              .filter(element => {
                const disabled = element.disabled
                  || element.getAttribute('aria-disabled') === 'true'
                  || /disabled/i.test(element.className || '');
                return !disabled;
              });

            const element = candidates[0];

            if (!element) {
              return false;
            }

            element.scrollIntoView({block: 'center'});
            element.click();
            element.dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
            element.dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
            element.dispatchEvent(new MouseEvent('click', {bubbles: true}));

            return true;
            """
        )

    def _has_free_cancellation_error(self):
        return self.driver.execute_script(
            """
            return [...document.querySelectorAll('div, span, p')]
              .some(element => /please select any one of the option/i.test(element.innerText || ''));
            """
        )