import os
from datetime import datetime

from utils.logger import LogGen

logger = LogGen.loggen()


try:
    import allure
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False


class ScreenshotUtil:

    @staticmethod
    def capture_screenshot(driver, screenshot_name="screenshot"):

        if driver is None:
            logger.error("Driver is None. Cannot capture screenshot.")
            return None

        screenshot_dir = os.path.join("reports", "screenshots")

        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        clean_name = screenshot_name.replace(" ", "_")

        screenshot_path = os.path.join(
            screenshot_dir,
            f"{clean_name}_{timestamp}.png"
        )

        driver.save_screenshot(screenshot_path)

        logger.info(f"Screenshot saved at: {screenshot_path}")

        # Attach to Allure only if available
        if ALLURE_AVAILABLE:
            allure.attach.file(
                screenshot_path,
                name=clean_name,
                attachment_type=allure.attachment_type.PNG
            )

        return screenshot_path