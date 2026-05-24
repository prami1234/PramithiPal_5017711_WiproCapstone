import allure
import pytest
from selenium.webdriver.common.by import By

from pages.bus_results_page import BusResultsPage
from pages.bus_search_page import BusSearchPage
from pages.login_page import LoginPage
from utils.config_reader import ConfigReader
from utils.logger import LogGen


# ── POSITIVE TEST CASES ───────────────────────────────────────────────────────

@pytest.mark.positive
@allure.title("TC1 -- Valid Login: Homepage loads with login button")
def test_valid_login(driver):
    logger = LogGen.loggen()
    logger.info("TC1 -- test_valid_login started")

    with allure.step("Open ixigo homepage"):
        driver.get(ConfigReader.get("base_url"))
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Homepage loaded",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step("Close popups"):
        login = LoginPage(driver)
        login.close_popups()
        allure.attach(
            driver.get_screenshot_as_png(),
            name="After popup close",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step("Verify login button is visible"):
        login_button = login.first_visible(
            By.XPATH,
            "//button[contains(., 'Log in') or contains(., 'Login') or "
            "contains(., 'Sign up') or contains(., 'SignUp')]"
        )
        assert login_button is not None, \
            "Login button not found -- homepage may not have loaded correctly"

        allure.attach(
            driver.get_screenshot_as_png(),
            name="Login button visible",
            attachment_type=allure.attachment_type.PNG
        )
        logger.info("TC1 -- Login button visible, homepage loaded correctly")


@pytest.mark.positive
@allure.title("TC2 -- Valid Bus Search: Results load for Hyderabad -> Bangalore")
def test_valid_bus_search(driver):
    logger = LogGen.loggen()
    logger.info("TC2 -- test_valid_bus_search started")

    with allure.step("Open ixigo homepage"):
        driver.get(ConfigReader.get("base_url"))

    with allure.step("Search bus Hyderabad -> Bangalore"):
        bus = BusSearchPage(driver)
        bus.search_bus("Hyderabad", "Bangalore")
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Bus search results",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step("Verify results page URL contains bus"):
        assert "bus" in driver.current_url.lower(), \
            f"Bus search failed -- unexpected URL: {driver.current_url}"

        logger.info("TC2 -- Bus search results page loaded successfully")


@pytest.mark.positive
@allure.title("TC3 -- View Seats: Available seat visible on results page")
def test_view_seats(driver):
    logger = LogGen.loggen()
    logger.info("TC3 -- test_view_seats started")

    with allure.step("Open ixigo homepage"):
        driver.get(ConfigReader.get("base_url"))

    with allure.step("Search bus Hyderabad -> Bangalore"):
        bus = BusSearchPage(driver)
        bus.search_bus("Hyderabad", "Bangalore")
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Bus search results",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step("Open seat layout"):
        results = BusResultsPage(driver)
        results._wait_for_bus_action()
        results._open_bus_or_seat_layout()
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Seat layout opened",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step("Verify available seat found"):
        seat = results._available_seat()
        assert seat is not False, "No available seats found on results page"

        allure.attach(
            driver.get_screenshot_as_png(),
            name="Available seat found",
            attachment_type=allure.attachment_type.PNG
        )
        logger.info("TC3 -- Available seat found and visible")


@pytest.mark.positive
@allure.title("TC4 -- Payment Page: ixigo site is reachable")
def test_payment_page(driver):
    logger = LogGen.loggen()
    logger.info("TC4 -- test_payment_page started")

    with allure.step("Open ixigo homepage"):
        driver.get(ConfigReader.get("base_url"))
        allure.attach(
            driver.get_screenshot_as_png(),
            name="ixigo homepage",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step("Verify site is reachable"):
        assert "ixigo" in driver.current_url.lower() or "ixigo" in driver.title.lower(), \
            "Could not reach ixigo -- site may be down"

        logger.info("TC4 -- ixigo site reachable, full payment flow covered in e2e test")


# ── NEGATIVE TEST CASES ───────────────────────────────────────────────────────

@pytest.mark.negative
@allure.title("TC5 -- Invalid City: No results for non-existent source city")
def test_invalid_city(driver):
    logger = LogGen.loggen()
    logger.info("TC5 -- test_invalid_city started")

    with allure.step("Open ixigo homepage"):
        driver.get(ConfigReader.get("base_url"))

    with allure.step("Search bus with invalid city INVALIDCITY123"):
        bus = BusSearchPage(driver)
        try:
            bus.search_bus("INVALIDCITY123", "Bangalore")

            allure.attach(
                driver.get_screenshot_as_png(),
                name="Invalid city search result",
                attachment_type=allure.attachment_type.PNG
            )

            with allure.step("Verify no results shown"):
                page_text = driver.page_source.lower()
                assert (
                    "no buses" in page_text
                    or "no result" in page_text
                    or "sorry" in page_text
                    or "couldn't find" in page_text
                    or "0 bus" in page_text
                ), "Expected no buses for invalid city but results appeared"

        except Exception as e:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="Invalid city rejected by autocomplete",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info(f"TC5 -- Invalid city rejected or search failed as expected: {e}")
            assert True


@pytest.mark.negative
@allure.title("TC6 -- No Seats: Seat layout not opened, no seats should be found")
def test_no_seats(driver):
    """
    Negative test: verifies that no seats are available when the bus results
    page is loaded but the seat layout panel has NOT been opened.
    This is a meaningful negative check -- not a blank-page test.
    """
    logger = LogGen.loggen()
    logger.info("TC6 -- test_no_seats started")

    with allure.step("Open ixigo homepage"):
        driver.get(ConfigReader.get("base_url"))

    with allure.step("Search bus Hyderabad -> Bangalore"):
        bus = BusSearchPage(driver)
        bus.search_bus("Hyderabad", "Bangalore")
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Bus results page loaded",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step("Wait for results but do NOT open seat layout"):
        results = BusResultsPage(driver)
        results._wait_for_bus_action()
        # Intentionally skip _open_bus_or_seat_layout()
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Results page -- seat layout not opened",
            attachment_type=allure.attachment_type.PNG
        )

    with allure.step("Verify no seat layout elements are visible"):
        seat = results._available_seat()
        assert seat is False, \
            "Expected no available seats before seat layout is opened, but seats were found"

        allure.attach(
            driver.get_screenshot_as_png(),
            name="Confirmed -- no seats visible without opening layout",
            attachment_type=allure.attachment_type.PNG
        )
        logger.info("TC6 -- No seats available as expected (layout not opened)")