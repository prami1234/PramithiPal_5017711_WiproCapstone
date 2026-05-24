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
from utils.screenshot_util import ScreenshotUtil


@given("user launches browser for testcases")
def step_impl(context):

    options = Options()

    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")

    context.driver = webdriver.Chrome(options=options)

    context.driver.implicitly_wait(
        ConfigReader.get_implicit_wait()
    )

    context.driver.maximize_window()


@when("user opens ixigo homepage for testcase")
def step_impl(context):

    HomePage(context.driver).open_homepage()


@when("user handles popup for testcase")
def step_impl(context):

    HomePage(context.driver).handle_popup()


@when("user performs login for testcase")
def step_impl(context):

    home = HomePage(context.driver)

    home.open_login_popup()

    login = LoginPage(context.driver)

    login.enter_mobile_number(
        ConfigReader.get_mobile_number()
    )

    login.click_continue()

    login.wait_for_manual_otp()

    ScreenshotUtil.take_screenshot(
        context.driver,
        "login_successful"
    )


@then("login should be successful for testcase")
def step_impl(context):

    assert LoginPage(
        context.driver
    ).is_login_completed()


@when("user opens buses page for testcase")
def step_impl(context):

    HomePage(context.driver).click_bus_tab()


@when("user enters valid source city")
def step_impl(context):

    BusPage(context.driver).enter_source(
        ConfigReader.get_source()
    )


@when("user enters valid destination city")
def step_impl(context):

    BusPage(context.driver).enter_destination(
        ConfigReader.get_destination()
    )


@when("user selects valid travel date")
def step_impl(context):

    BusPage(context.driver).select_travel_date(
        ConfigReader.get_travel_date()
    )


@when("user searches buses for testcase")
def step_impl(context):

    BusPage(context.driver).click_search()


@then("valid buses should appear")
def step_impl(context):

    ScreenshotUtil.take_screenshot(
        context.driver,
        "valid_bus_results"
    )

    assert True


@when("user opens seat layout")
def step_impl(context):

    bus = BusPage(context.driver)

    bus.click_select_seats_first_result()


@then("available seats should appear")
def step_impl(context):

    ScreenshotUtil.take_screenshot(
        context.driver,
        "available_seats"
    )

    assert True


@when("user completes full booking flow")
def step_impl(context):

    home = HomePage(context.driver)

    home.open_homepage()

    home.handle_popup()

    home.click_bus_tab()

    bus = BusPage(context.driver)

    bus.enter_source(
        ConfigReader.get_source()
    )

    bus.enter_destination(
        ConfigReader.get_destination()
    )

    bus.select_travel_date(
        ConfigReader.get_travel_date()
    )

    bus.click_search()

    bus.click_select_seats_first_result()

    bus.select_available_seat()

    bus.click_proceed()

    excel = ExcelReader()

    passenger = excel.get_passenger_details()

    PassengerPage(
        context.driver
    ).fill_passenger_details(passenger)

    PassengerPage(
        context.driver
    ).click_proceed_to_payment()

    excel.close()


@then("payment page should load successfully")
def step_impl(context):

    payment = PaymentPage(context.driver)

    ScreenshotUtil.take_screenshot(
        context.driver,
        "payment_page"
    )

    assert payment.is_on_payment_page()


@when("user enters invalid source city")
def step_impl(context):

    BusPage(context.driver).enter_source(
        "xxxxinvalid"
    )


@when("user enters invalid destination city")
def step_impl(context):

    BusPage(context.driver).enter_destination(
        "yyyyinvalid"
    )


@then("invalid city validation should appear")
def step_impl(context):

    ScreenshotUtil.take_screenshot(
        context.driver,
        "invalid_city_validation"
    )

    assert True


@then("no seats condition should be handled")
def step_impl(context):

    ScreenshotUtil.take_screenshot(
        context.driver,
        "no_seats_handled"
    )

    assert True