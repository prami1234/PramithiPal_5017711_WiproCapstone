from behave import given, when, then
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config.config_reader import ConfigReader
from pages.bus_page import BusPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.passenger_page import PassengerPage
from pages.payment_page import PaymentPage
from utils.excel_reader import ExcelReader


@given("user launches the browser")
def step_impl(context):
    options = Options()
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    if ConfigReader.is_headless():
        options.add_argument("--headless=new")

    context.driver = webdriver.Chrome(options=options)
    context.driver.implicitly_wait(ConfigReader.get_implicit_wait())
    context.driver.set_page_load_timeout(ConfigReader.get_page_load_timeout())
    context.driver.maximize_window()


@when("user opens ixigo homepage")
def step_impl(context):
    HomePage(context.driver).open_homepage()


@when("user handles the homepage popup")
def step_impl(context):
    HomePage(context.driver).handle_popup()


@when("user logs in with mobile number")
def step_impl(context):
    HomePage(context.driver).open_login_popup()
    login_page = LoginPage(context.driver)
    login_page.enter_mobile_number(ConfigReader.get_mobile_number())
    login_page.click_continue()


@when("user completes otp manually")
def step_impl(context):
    LoginPage(context.driver).wait_for_manual_otp()


@then("user should be logged in or login modal should be closed")
def step_impl(context):
    assert LoginPage(context.driver).is_login_completed(), (
        "Login was not completed. Enter the OTP manually in the browser before the timeout."
    )


@when("user opens bus section")
def step_impl(context):
    HomePage(context.driver).click_bus_tab()


@when("user enters source city")
def step_impl(context):
    BusPage(context.driver).enter_source(ConfigReader.get_source())


@when("user enters destination city")
def step_impl(context):
    BusPage(context.driver).enter_destination(ConfigReader.get_destination())


@when("user selects travel date")
def step_impl(context):
    BusPage(context.driver).select_travel_date(ConfigReader.get_travel_date())


@when("user searches buses")
def step_impl(context):
    BusPage(context.driver).click_search()


@when("user applies bus filters")
def step_impl(context):
    BusPage(context.driver).apply_filters(
        bus_type=ConfigReader.get_bus_type_filter(),
        departure_time=ConfigReader.get_departure_time_filter(),
    )


@when("user selects seat")
def step_impl(context):
    bus_page = BusPage(context.driver)
    bus_page.click_select_seats_first_result()
    bus_page.select_available_seat()


@when("user continues booking")
def step_impl(context):
    BusPage(context.driver).click_proceed()


@when("user enters passenger details")
def step_impl(context):
    excel = ExcelReader()
    try:
        passenger_data = excel.get_passenger_details()
    except Exception:
        passenger_data = ConfigReader.get_passenger_defaults()
    finally:
        excel.close()

    PassengerPage(context.driver).fill_passenger_details(passenger_data)


@when("user proceeds to payment")
def step_impl(context):
    PassengerPage(context.driver).click_proceed_to_payment()


@then("payment page should open")
def step_impl(context):
    payment_page = PaymentPage(context.driver)
    assert payment_page.is_on_payment_page(), "Payment page not loaded"
    payment_page.capture_payment_page()


@then("user closes the browser")
def step_impl(context):
    context.driver.quit()
    context.driver = None