from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout, ignored_exceptions=(StaleElementReferenceException,))

    def js_click(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        try:
            element.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            self.driver.execute_script("arguments[0].click();", element)

    def close_popups(self):
        try:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass

        self.driver.execute_script(
            "document.querySelectorAll('.abrs-backdrop').forEach(e => e.remove());"
            "document.body.style.overflow = 'auto';"
        )

        close_xpaths = [
            "//button[@aria-label='Close']",
            "//*[@aria-label='Close']",
            "//*[@aria-label='close']",
            "//button[contains(., 'Close')]",
            "//button[contains(., 'Skip')]",
            "//button[contains(., 'Later')]",
            "//*[contains(@class, 'close') or contains(@class, 'Close')]",
            "//*[contains(@class, 'cross') or contains(@class, 'Cross')]",
            "//*[@role='button' and (contains(., 'Close') or contains(., 'Skip') or contains(., 'Later'))]",
        ]

        for xpath in close_xpaths:
            try:
                close_button = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                self.js_click(close_button)
                break
            except TimeoutException:
                continue

        self.driver.execute_script("""
            const offerWords = ['book now', 'flat', 'off', 'coupon', 'code'];
            const nodes = Array.from(document.querySelectorAll('div, section, aside'));

            for (const node of nodes) {
                const text = (node.innerText || '').toLowerCase();
                const style = window.getComputedStyle(node);
                const rect = node.getBoundingClientRect();

                const isOverlay =
                    ['fixed', 'absolute'].includes(style.position) &&
                    rect.width > 250 &&
                    rect.height > 150 &&
                    rect.top >= 0 &&
                    rect.left >= 0;

                const looksLikeOffer = offerWords.some(word => text.includes(word));
                const looksLikeLogin = text.includes('log in to ixigo') || text.includes('enter mobile number');

                if (isOverlay && looksLikeOffer && !looksLikeLogin) {
                    node.remove();
                }
            }

            document.body.style.overflow = 'auto';
        """)

    def visible_elements(self, by, locator):
        result = []
        for element in self.driver.find_elements(by, locator):
            try:
                if element.is_displayed() and element.is_enabled():
                    result.append(element)
            except StaleElementReferenceException:
                continue
        return result

    def first_visible(self, by, locator):
        return self.wait.until(
            lambda driver: next(
                (
                    element for element in driver.find_elements(by, locator)
                    if element.is_displayed() and element.is_enabled()
                ),
                False
            )
        )

    def click_first_visible(self, by, locator):
        element = self.first_visible(by, locator)
        self.js_click(element)
        return element

    def page_text(self):
        return self.driver.find_element(By.TAG_NAME, "body").text