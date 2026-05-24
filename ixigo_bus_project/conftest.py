import sys
import io
import logging
import os

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Force UTF-8 output on Windows to handle arrows, rupee symbols etc.
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def pytest_configure(config):
    os.makedirs("reports/screenshots", exist_ok=True)
    os.makedirs("reports/allure-results", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    logging.getLogger("WDM").setLevel(logging.WARNING)


def allure_step_screenshot(driver, step_name: str):
    with allure.step(step_name):
        allure.attach(
            driver.get_screenshot_as_png(),
            name=step_name,
            attachment_type=allure.attachment_type.PNG
        )


@pytest.fixture(scope="function")
def driver(request):
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )
    driver.maximize_window()
    driver.set_page_load_timeout(60)
    driver.step = lambda name: allure_step_screenshot(driver, name)

    yield driver

    test_name = request.node.name
    if hasattr(request.node, "rep_call"):
        status = (
            "FAILED" if request.node.rep_call.failed
            else "PASSED" if request.node.rep_call.passed
            else "OTHER"
        )
    else:
        status = "UNKNOWN"

    screenshot_path = f"reports/screenshots/{test_name}_{status}.png"
    driver.save_screenshot(screenshot_path)
    allure.attach.file(
        screenshot_path,
        name=f"Final — {test_name} [{status}]",
        attachment_type=allure.attachment_type.PNG
    )
    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)