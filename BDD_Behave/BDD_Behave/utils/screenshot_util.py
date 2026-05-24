import os
from datetime import datetime

from config.config_reader import ConfigReader
from utils.logger import get_logger

logger = get_logger(__name__)


class ScreenshotUtil:
    @staticmethod
    def take_screenshot(driver, page_name):
        try:
            screenshots_dir = ConfigReader.get_screenshots_path()
            os.makedirs(screenshots_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{page_name}_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)

            driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as error:
            logger.error(f"Failed to take screenshot for '{page_name}': {error}")
            return None

    @staticmethod
    def take_full_page_screenshot(driver, page_name):
        try:
            screenshots_dir = ConfigReader.get_screenshots_path()
            os.makedirs(screenshots_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{page_name}_fullpage_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)

            driver.execute_script("window.scrollTo(0, 0);")
            driver.save_screenshot(filepath)
            logger.info(f"Full page screenshot saved: {filepath}")
            return filepath
        except Exception as error:
            logger.error(f"Failed to take full-page screenshot for '{page_name}': {error}")
            return None