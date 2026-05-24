import time
from urllib.parse import quote

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from utils.logger import get_logger
from utils.screenshot_util import ScreenshotUtil
from utils.waits import Waits

logger = get_logger(__name__)


class BusPage:
    SOURCE_INPUT = (By.XPATH, "//input[@placeholder='Leaving From']")
    DESTINATION_INPUT = (By.XPATH, "//input[@placeholder='Going To']")
    DATE_INPUT = (By.XPATH, "//input[@placeholder='Onward Journey Date']")
    AUTOCOMPLETE_FIRST = (By.XPATH, "(//li[contains(@class,'auto-complete-list-item')])[1]")
    SEARCH_BUTTON = (By.XPATH, "//div[@id='search-button']//a[normalize-space()='Search' or normalize-space()='Search Buses']")
    RESULT_COUNT = (By.XPATH, "//*[contains(.,'Showing') and contains(.,'Buses on this route')]")
    NO_BUSES = (By.XPATH, "//*[contains(.,'No Buses found')]")
    SELECT_SEATS_FIRST = (By.XPATH, "(//button[normalize-space()='Select Seats'])[1]")
    AVAILABLE_SEAT = (By.XPATH, "(//div[@id='seat-layout-container']//button[contains(@class,'seat') and not(contains(@class,'booked'))])[1]")
    PROCEED_BUTTON = (By.XPATH, "//button[normalize-space()='Proceed'] | //a[normalize-space()='Proceed']")
    DROPPING_TAB = (By.XPATH, "//a[contains(.,'Dropping Points')] | //button[contains(.,'Dropping Points')]")

    CITY_IDS = {
        "jaipur": "241",
        "delhi": "344",
        "kolkata": "163",
        "mumbai": "331",
        "hyderabad": "3",
        "bangalore": "7",
        "bengaluru": "7",
        "chennai": "123",
        "pune": "130",
        "ahmedabad": "256",
    }

    def __init__(self, driver):
        self.driver = driver
        self.waits = Waits(driver)

    def _type_city_and_select_first(self, locator, city, field_name):
        logger.info("Entering %s city: %s", field_name, city)
        city_input = self.waits.wait_for_element_clickable(*locator, timeout=25)
        city_input.click()
        city_input.send_keys(Keys.CONTROL, "a")
        city_input.send_keys(Keys.BACKSPACE)
        city_input.send_keys(city)

        option = self.waits.wait_for_element_clickable(*self.AUTOCOMPLETE_FIRST, timeout=20)
        self.waits.js_click(option)

        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(1)

        ScreenshotUtil.take_screenshot(self.driver, f"{field_name.lower()}_city_selected")

    def enter_source(self, source):
        self.driver.ixigo_source_city = source
        self._type_city_and_select_first(self.SOURCE_INPUT, source, "Source")

    def enter_destination(self, destination):
        self.driver.ixigo_destination_city = destination
        self._type_city_and_select_first(self.DESTINATION_INPUT, destination, "Destination")

    def select_travel_date(self, date_str):
        logger.info("Selecting travel date: %s", date_str)

        self.driver.ixigo_travel_date = date_str

        date_input = self.waits.wait_for_element_present(*self.DATE_INPUT, timeout=15)

        self.driver.execute_script(
            "arguments[0].removeAttribute('readonly');"
            "arguments[0].value = arguments[1];"
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
            date_input,
            date_str,
        )

        time.sleep(1)
        ScreenshotUtil.take_screenshot(self.driver, "travel_date_selected")

    def click_search(self):
        logger.info("Searching buses")

        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(1)

        self.waits.wait_for_element_present(*self.SEARCH_BUTTON, timeout=20)
        search_buttons = self.driver.find_elements(*self.SEARCH_BUTTON)
        search_button = next((button for button in search_buttons if button.is_displayed()), search_buttons[0])

        before_url = self.driver.current_url

        self.waits.js_click(search_button)
        time.sleep(6)

        if self.driver.current_url == before_url:
            try:
                search_button.click()
            except Exception:
                self._open_search_url_directly()
            time.sleep(6)

        if self.driver.current_url == before_url:
            self._open_search_url_directly()
            time.sleep(8)

        if self.waits.is_element_present(*self.NO_BUSES, timeout=3):
            ScreenshotUtil.take_screenshot(self.driver, "no_buses_found")
            raise AssertionError("No buses found for the selected route/date. Use a working route such as Jaipur to Delhi.")

        if not self.waits.is_element_present(*self.RESULT_COUNT, timeout=30):
            ScreenshotUtil.take_screenshot(self.driver, "bus_search_not_loaded")
            raise AssertionError("Bus search results did not load after clicking Search.")

        ScreenshotUtil.take_screenshot(self.driver, "bus_search_results")

    def _open_search_url_directly(self):
        source = getattr(self.driver, "ixigo_source_city", "")
        destination = getattr(self.driver, "ixigo_destination_city", "")
        date_str = getattr(self.driver, "ixigo_travel_date", "")

        source_id = self.CITY_IDS.get(source.lower())
        destination_id = self.CITY_IDS.get(destination.lower())

        if not all([source, destination, date_str, source_id, destination_id]):
            return

        day, month, year = date_str.split("/")
        travel_date = f"{day}-{month}-{year}"

        url = (
            "https://www.ixigo.com/buses/bus_search/"
            f"{quote(source)}/{source_id}/{quote(destination)}/{destination_id}/{travel_date}/O"
        )

        logger.info("Opening bus search URL directly: %s", url)
        self.driver.get(url)

    def apply_filters(self, bus_type=None, departure_time=None):
        logger.info("Applying filters: %s, %s", bus_type, departure_time)

        if bus_type:
            self._click_filter_chip(bus_type)

        if departure_time:
            self._click_filter_chip(departure_time)

        time.sleep(3)
        ScreenshotUtil.take_screenshot(self.driver, "bus_filters_applied")

    def _click_filter_chip(self, visible_text):
        chip = self.waits.wait_for_element_clickable(
            By.XPATH,
            f"//a[normalize-space()='{visible_text}'] | //button[normalize-space()='{visible_text}']",
            timeout=15,
        )

        self.waits.scroll_to_element(chip)
        self.waits.js_click(chip)
        time.sleep(2)

    def click_select_seats_first_result(self):
        logger.info("Opening seat layout for first bus")

        button = self.waits.wait_for_element_clickable(*self.SELECT_SEATS_FIRST, timeout=30)
        self.waits.scroll_to_element(button)
        self.waits.js_click(button)

        self.waits.wait_for_element_present(By.ID, "seat-layout-container", timeout=30)
        ScreenshotUtil.take_screenshot(self.driver, "seat_layout_opened")

    def select_available_seat(self):
        logger.info("Selecting first available seat")

        seat = self.waits.wait_for_element_clickable(*self.AVAILABLE_SEAT, timeout=30)
        self.waits.scroll_to_element(seat)
        self.waits.js_click(seat)

        time.sleep(2)
        ScreenshotUtil.take_screenshot(self.driver, "seat_selected")

    def click_proceed(self):
        logger.info("Proceeding after seat selection")

        self._select_boarding_and_dropping_points()

        proceed = self.waits.wait_for_element_clickable(*self.PROCEED_BUTTON, timeout=20)
        self.waits.scroll_to_element(proceed)
        self.waits.js_click(proceed)

        time.sleep(5)
        ScreenshotUtil.take_screenshot(self.driver, "after_seat_proceed")

    def _select_boarding_and_dropping_points(self):
        logger.info("Selecting boarding and dropping points")

        self._click_first_visible_radio_like("boarding")

        if self.waits.is_element_present(*self.DROPPING_TAB, timeout=5):
            try:
                dropping_tab = self.waits.wait_for_element_clickable(*self.DROPPING_TAB, timeout=5)
                self.waits.js_click(dropping_tab)
                time.sleep(1)
                self._click_first_visible_radio_like("dropping")
            except Exception as error:
                logger.warning("Dropping point selection skipped: %s", error)

        ScreenshotUtil.take_screenshot(self.driver, "boarding_dropping_selected")

    def _click_first_visible_radio_like(self, point_type):
        clicked = self.driver.execute_script(
            """
            const selectors = [
              'input[type="radio"]',
              '[role="radio"]',
              'button[class*="radio"]',
              'div[class*="radio"]',
              'span[class*="radio"]'
            ];

            const elements = selectors.flatMap(selector => [...document.querySelectorAll(selector)]);

            const visible = elements.find(element => {
              const rect = element.getBoundingClientRect();
              const style = window.getComputedStyle(element);

              return rect.width > 0
                && rect.height > 0
                && rect.top >= 0
                && rect.top < window.innerHeight
                && style.visibility !== 'hidden'
                && style.display !== 'none';
            });

            if (visible) {
              visible.scrollIntoView({block: 'center'});
              visible.click();
              return true;
            }

            return false;
            """
        )

        if clicked:
            time.sleep(1)
            logger.info("%s point selected", point_type.capitalize())
        else:
            logger.warning("No visible %s point radio found", point_type)