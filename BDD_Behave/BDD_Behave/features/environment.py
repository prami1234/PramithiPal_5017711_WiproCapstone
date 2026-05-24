from utils.screenshot_util import ScreenshotUtil

try:
    import allure
except Exception:
    allure = None


def after_step(context, step):
    if step.status == "failed" and hasattr(context, "driver") and context.driver:
        screenshot_path = ScreenshotUtil.take_screenshot(context.driver, "failed_step")
        if allure and screenshot_path:
            allure.attach.file(
                screenshot_path,
                name="failed_step",
                attachment_type=allure.attachment_type.PNG,
            )


def after_scenario(context, scenario):
    if hasattr(context, "driver") and context.driver:
        context.driver.quit()
        context.driver = None