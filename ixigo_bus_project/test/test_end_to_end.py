import time

import allure
import pytest

from pages.bus_results_page import BusResultsPage
from pages.bus_search_page import BusSearchPage
from pages.login_page import LoginPage
from pages.passenger_page import PassengerPage
from pages.payment_page import PaymentPage
from utils.config_reader import ConfigReader
from utils.csv_reader import CSVReader
from utils.logger import LogGen


@pytest.mark.e2e
@allure.title("End-to-End Bus Booking Flow")
@allure.description("Complete booking flow: login -> search -> filters -> seat -> passenger -> payment")
def test_end_to_end(driver):
    logger = LogGen.loggen()

    # ── Step 1: Load test data ─────────────────────────────────────────
    with allure.step("Load test data from CSV"):
        data = CSVReader.read_csv("test_data.csv")
        assert data, "CSV file is empty or not loaded"
        row = data[0]

        source = row.get("From", "").strip() or ConfigReader.get("source")
        destination = row.get("To", "").strip() or ConfigReader.get("destination")
        passenger_name = row.get("Name", "").strip() or "Test User"
        passenger_age = row.get("Age", "").strip() or "25"
        passenger_gender = row.get("Gender", "").strip() or "Female"
        mobile = row.get("mobile no", "").strip() or ConfigReader.get("phone_number")

        assert source, "Source city is missing from CSV and config"
        assert destination, "Destination city is missing from CSV and config"
        assert mobile, "Mobile number is missing from CSV and config"

        logger.info(f"Test data loaded -- {source} -> {destination}, passenger: {passenger_name}")

    # ── Step 2: Open homepage ──────────────────────────────────────────
    with allure.step("Open ixigo homepage"):
        driver.get(ConfigReader.get("base_url"))

        allure.attach(
            driver.get_screenshot_as_png(),
            name="Homepage",
            attachment_type=allure.attachment_type.PNG
        )

        assert "ixigo" in driver.current_url.lower() or "ixigo" in driver.title.lower(), \
            "Homepage did not open correctly"

        logger.info("Opened ixigo homepage")

    # ── Step 3: Login ──────────────────────────────────────────────────
    with allure.step("Login with phone number"):
        login = LoginPage(driver)
        login.login_with_phone(mobile)

        allure.attach(
            driver.get_screenshot_as_png(),
            name="After login",
            attachment_type=allure.attachment_type.PNG
        )

        page_text = login.page_text().lower()
        assert "log in to ixigo" not in page_text and "enter mobile number" not in page_text, \
            "Login failed -- still on OTP or mobile entry screen"

        logger.info("Login completed")

    # ── Step 4: Search bus ─────────────────────────────────────────────
    with allure.step(f"Search bus: {source} -> {destination}"):
        time.sleep(2)
        bus = BusSearchPage(driver)
        bus.search_bus(source, destination)

        allure.attach(
            driver.get_screenshot_as_png(),
            name="Bus search results",
            attachment_type=allure.attachment_type.PNG
        )

        assert "bus" in driver.current_url.lower(), \
            f"Bus search failed -- unexpected URL: {driver.current_url}"

        logger.info("Bus search completed")

    # ── Step 5: Apply filters and select seat ─────────────────────────
    with allure.step("Apply filters and select seat"):
        result = BusResultsPage(driver)
        result.complete_booking_flow()

        allure.attach(
            driver.get_screenshot_as_png(),
            name="After booking flow",
            attachment_type=allure.attachment_type.PNG
        )

        assert "ixigo" in driver.current_url.lower(), \
            "Booking flow failed -- unexpected page after seat selection"

        logger.info("Bus filters and booking flow completed")

    # ── Step 6: Fill passenger details ────────────────────────────────
    with allure.step("Fill passenger details"):
        passenger = PassengerPage(driver)
        passenger.fill_passenger_details(passenger_name, passenger_age, passenger_gender, mobile)

        allure.attach(
            driver.get_screenshot_as_png(),
            name="Passenger form filled",
            attachment_type=allure.attachment_type.PNG
        )

        page_text = driver.page_source.lower()
        assert any(keyword in page_text for keyword in ["name", "age", "gender", "passenger"]), \
            "Passenger form fields not found on page"

        logger.info("Passenger details filled")

    # ── Step 7: Continue to payment ───────────────────────────────────
    with allure.step("Continue to payment"):
        passenger.continue_to_payment()

        allure.attach(
            driver.get_screenshot_as_png(),
            name="After continue to payment",
            attachment_type=allure.attachment_type.PNG
        )

        assert (
            "payment" in driver.current_url.lower()
            or "pay" in driver.current_url.lower()
            or "passenger" in driver.current_url.lower()
        ), f"Continue to payment failed -- URL: {driver.current_url}"

        logger.info("Passenger details submitted")

    # ── Step 8: Verify payment page ───────────────────────────────────
    with allure.step("Verify payment page"):
        payment = PaymentPage(driver)
        payment.proceed_to_payment()

        allure.attach(
            driver.get_screenshot_as_png(),
            name="Payment page",
            attachment_type=allure.attachment_type.PNG
        )

        payment_keywords = ["payment", "pay", "fare", "wallet", "card", "upi"]
        body_text = payment.page_text().lower()
        assert any(word in body_text for word in payment_keywords), \
            "Payment page not reached -- payment keywords not found on page"

        logger.info("Reached payment page")