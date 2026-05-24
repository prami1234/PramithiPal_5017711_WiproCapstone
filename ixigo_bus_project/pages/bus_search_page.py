import time

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.logger import LogGen

logger = LogGen.loggen(__name__)


class BusSearchPage(BasePage):

    def open_buses(self):
        self.close_popups()
        time.sleep(2)
        self.close_popups()

        bus_links = self.visible_elements(
            By.XPATH,
            "//a[contains(@href, '/buses') and contains(., 'Buses')]"
        )

        if bus_links:
            try:
                self.driver.execute_script("arguments[0].click();", bus_links[0])
            except Exception:
                self.driver.get("https://www.ixigo.com/buses")
        else:
            self.driver.get("https://www.ixigo.com/buses")

        try:
            self.wait.until(EC.url_contains("/buses"))
        except Exception:
            self.driver.get("https://www.ixigo.com/buses")
            self.wait.until(EC.url_contains("/buses"))

        self.close_popups()
        logger.info("Bus tab opened")

    def _select_city(self, placeholder, city):
        city_input = self.first_visible(By.XPATH, f"//input[@placeholder='{placeholder}']")
        city_input.clear()
        city_input.send_keys(city)

        option = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "li.auto-complete-list-item"))
        )
        self.js_click(option)
        logger.info(f"{placeholder} selected: {city}")

    def search_bus(self, source, destination):
        with allure.step(f"Search bus: {source} -> {destination}"):
            self.open_buses()

            self._select_city("Leaving From", source)
            self._select_city("Going To", destination)

            tomorrow_buttons = self.visible_elements(
                By.XPATH, "//*[normalize-space()='Tomorrow']"
            )
            if tomorrow_buttons:
                self.js_click(tomorrow_buttons[0])
                logger.info("Tomorrow's date selected")

            search_buttons = self.visible_elements(
                By.XPATH,
                "//*[normalize-space()='Search' and contains(@class, 'btn-search-wrapper')]"
            )
            if search_buttons:
                self.js_click(search_buttons[0])
            else:
                self.click_first_visible(By.XPATH, "//*[normalize-space()='Search']")

            logger.info(f"Search clicked for {source} -> {destination}")

            self.wait.until(
                lambda driver: "bus_search" in driver.current_url
                or self.visible_elements(
                    By.XPATH,
                    "//*[normalize-space()='View Buses' or normalize-space()='Select Seats']"
                )
            )

            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=f"Bus search results -- {source} to {destination}",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"Bus search results loaded for {source} -> {destination}")