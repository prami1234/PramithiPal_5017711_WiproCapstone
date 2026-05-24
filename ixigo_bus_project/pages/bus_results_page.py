import allure
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage
from utils.logger import LogGen

logger = LogGen.loggen(__name__)


class BusResultsPage(BasePage):

    def apply_filters(self):
        with allure.step("Apply filters: AC, Sleeper, Time slot"):
            self.close_popups()

            self._click_filter_option(["ac"], timeout=5)
            self._click_filter_option(["sleeper", "seater"], timeout=5)
            self._click_filter_option(["5 pm - 11 pm", "10 am - 5 pm", "after 11 pm"], timeout=5)

            self._open_filter_section_fast("Bus Partner")
            self._open_filter_section_fast("Boarding Point")
            self._open_filter_section_fast("Dropping Point")

            self.driver.execute_script("window.scrollTo(0, 0);")
            self._wait_for_bus_action()

            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Filters applied",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info("Filters applied: AC, Sleeper, time slot, sections opened")

    def select_bus_and_seat(self):
        with allure.step("Select seat and proceed"):
            self.close_popups()
            self.driver.execute_script("window.scrollTo(0, 0);")

            if self._available_seat():
                logger.info("Seat layout already open")
            else:
                self._open_bus_or_seat_layout()

            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Seat layout opened",
                attachment_type=allure.attachment_type.PNG
            )

            proceed = self._select_one_priced_seat_and_get_proceed()

            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="Seat selected",
                attachment_type=allure.attachment_type.PNG
            )

            self.js_click(proceed)
            logger.info("Seat selected and Proceed clicked")

            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="After Proceed clicked",
                attachment_type=allure.attachment_type.PNG
            )

    def complete_booking_flow(self):
        self.apply_filters()
        self.select_bus_and_seat()

    def _click_filter_option(self, filter_names, timeout=5):
        for name in filter_names:
            try:
                option = WebDriverWait(self.driver, timeout).until(
                    lambda driver: self._fresh_visible(
                        "//*[translate(normalize-space(.), "
                        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')="
                        f"'{name}']"
                    )
                )
                self.js_click(option)
                logger.info(f"Filter selected: {name}")
                return True
            except TimeoutException:
                continue
        return False

    def _open_filter_section_fast(self, section_name):
        try:
            section = WebDriverWait(self.driver, 2).until(
                lambda driver: self._fresh_visible(
                    f"//*[normalize-space()='{section_name}']"
                )
            )
            self.js_click(section)
            logger.info(f"Filter section opened: {section_name}")
            return True
        except TimeoutException:
            return False

    def _open_bus_or_seat_layout(self):
        select_seats = self._fresh_visible("//*[normalize-space()='Select Seats']")
        if select_seats:
            self.js_click(select_seats)
            logger.info("Select Seats clicked")
            self.wait.until(lambda driver: self._available_seat())
            return

        view_buses = self._fresh_visible("//*[normalize-space()='View Buses']")
        if view_buses:
            self.js_click(view_buses)
            logger.info("View Buses clicked")

        select_seats = self.wait.until(
            lambda driver: self._fresh_visible("//*[normalize-space()='Select Seats']")
        )
        self.js_click(select_seats)
        logger.info("Select Seats clicked after View Buses")
        self.wait.until(lambda driver: self._available_seat())

    def _select_one_priced_seat_and_get_proceed(self):
        seat = self.wait.until(lambda driver: self._available_seat())
        self.js_click(seat)
        logger.info(f"Seat selected: {seat.text.strip()}")

        self.driver.execute_script("window.scrollBy(0, 650);")
        self._select_boarding_and_dropping_if_needed()

        proceed_xpath = (
            "//button[contains(normalize-space(.), 'Proceed')]"
            " | //a[contains(normalize-space(.), 'Proceed')]"
            " | //*[@role='button' and contains(normalize-space(.), 'Proceed')]"
            " | //*[contains(@class, 'btn') and contains(normalize-space(.), 'Proceed')]"
        )
        return self.wait.until(EC.element_to_be_clickable((By.XPATH, proceed_xpath)))

    def _select_boarding_and_dropping_if_needed(self):
        self._click_first_boarding_or_dropping_item()
        dropping_tab_clicked = self._click_first_visible_fast(
            "//*[normalize-space()='Dropping Points' or "
            "normalize-space()='Dropping Point']"
        )
        if dropping_tab_clicked:
            self._click_first_boarding_or_dropping_item()

    def _click_first_boarding_or_dropping_item(self):
        item = self.driver.execute_script("""
            const visible = (el) => {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                return rect.width > 80 && rect.height > 15 &&
                    style.visibility !== 'hidden' && style.display !== 'none';
            };
            const containers = Array.from(
                document.querySelectorAll('.seating-place-selector')
            ).filter(visible);
            for (const container of containers) {
                const candidates = Array.from(
                    container.querySelectorAll('li, label, button, a, div')
                ).filter((el) => {
                    const text = (el.innerText || '').trim().toLowerCase();
                    if (!visible(el) || !text) return false;
                    if (['boarding points','dropping points',
                         'boarding point','dropping point'].includes(text)) return false;
                    if (text.includes('seat(s)') || text.includes('proceed')) return false;
                    return true;
                });
                candidates.sort((a, b) =>
                    a.getBoundingClientRect().top - b.getBoundingClientRect().top
                );
                if (candidates.length) return candidates[0];
            }
            return null;
        """)
        if item:
            self.js_click(item)
            return True
        return False

    def _click_first_visible_fast(self, xpath):
        try:
            element = WebDriverWait(self.driver, 2).until(
                lambda driver: self._fresh_visible(xpath)
            )
            self.js_click(element)
            return True
        except TimeoutException:
            return False

    def _available_seat(self):
        for seat in self.driver.find_elements(By.CSS_SELECTOR, "button.seat"):
            try:
                seat_class = (seat.get_attribute("class") or "").lower()
                seat_text = seat.text.strip()
                if (
                    seat.is_displayed() and seat.is_enabled()
                    and seat_text
                    and any(char.isdigit() for char in seat_text)
                    and "booked" not in seat_class
                    and "sold" not in seat_class
                    and "unavailable" not in seat_class
                    and "disabled" not in seat_class
                    and "selected" not in seat_class
                ):
                    return seat
            except StaleElementReferenceException:
                continue
        return False

    def _wait_for_bus_action(self):
        return self.wait.until(
            lambda driver: self._fresh_visible("//*[normalize-space()='Select Seats']")
            or self._fresh_visible("//*[normalize-space()='View Buses']")
            or self._available_seat()
        )

    def _fresh_visible(self, xpath):
        try:
            return next(
                (
                    el for el in self.driver.find_elements(By.XPATH, xpath)
                    if el.is_displayed() and el.is_enabled()
                ),
                False
            )
        except StaleElementReferenceException:
            return False