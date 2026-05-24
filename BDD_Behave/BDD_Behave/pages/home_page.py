import time

from selenium.webdriver.common.by import By

from config.config_reader import ConfigReader
from utils.logger import get_logger
from utils.screenshot_util import ScreenshotUtil
from utils.waits import Waits

logger = get_logger(__name__)


class HomePage:
    LOGIN_LINKS = [
        (By.ID, "login-link"),
        (By.XPATH, "//button[normalize-space()='Log in/Sign up']"),
        (By.XPATH, "//*[@role='button' and contains(normalize-space(),'Log in/Sign up')]"),
        (By.XPATH, "//*[normalize-space()='Login/SignUp' or normalize-space()='Log in/Sign up']"),
    ]
    BUS_LINK = (By.XPATH, "//a[contains(@href,'/buses') and normalize-space()='Buses']")
    CLOSE_POPUP = (By.XPATH, "//button[contains(@aria-label,'close') or contains(.,'Close') or contains(.,'Skip')]")

    def __init__(self, driver):
        self.driver = driver
        self.waits = Waits(driver)
        self.url = ConfigReader.get_base_url()

    def open_homepage(self):
        logger.info("Opening ixigo homepage")
        self.driver.get(self.url)
        self.waits.wait_for_page_ready()
        ScreenshotUtil.take_screenshot(self.driver, "homepage_opened")

    def handle_popup(self):
        logger.info("Handling popup if present")
        try:
            close_button = self.waits.find_first_clickable(self.CLOSE_POPUP, timeout=3)
            close_button.click()
            time.sleep(1)
            ScreenshotUtil.take_screenshot(self.driver, "homepage_popup_closed")
            return True
        except Exception:
            logger.info("No closable homepage popup found")
            return False

    def open_login_popup(self):
        logger.info("Opening login popup")
        mobile_locator = "//input[@placeholder='Mobile no.' or @placeholder='Enter Mobile Number']"
        if self.waits.is_element_present(By.XPATH, mobile_locator, timeout=2):
            return

        try:
            login_button = self.waits.find_first_clickable(self.LOGIN_LINKS, timeout=5)
            self.waits.js_click(login_button)
        except Exception:
            self.driver.execute_script(
                """
                const candidates = [...document.querySelectorAll('button,a,div[role="button"],div')]
                  .filter(e => (e.innerText || '').trim().toLowerCase().includes('log in'));
                const visible = candidates.find(e => {
                  const r = e.getBoundingClientRect();
                  return r.width > 0 && r.height > 0;
                });
                if (visible) visible.click();
                """
            )
        self.waits.wait_for_element_visible(By.XPATH, mobile_locator, timeout=15)
        ScreenshotUtil.take_screenshot(self.driver, "login_popup_opened")

    def click_bus_tab(self):
        logger.info("Clicking Buses tab")
        try:
            bus_tab = self.waits.wait_for_element_clickable(*self.BUS_LINK, timeout=15)
            self.waits.js_click(bus_tab)
        except Exception:
            logger.warning("Buses tab click failed. Opening buses URL as fallback.")
            self.driver.get(f"{self.url.rstrip('/')}/buses")
        self.waits.wait_for_page_ready()
        self.waits.wait_for_element_visible(By.XPATH, "//input[@placeholder='Leaving From']", timeout=25)
        ScreenshotUtil.take_screenshot(self.driver, "buses_page_opened")