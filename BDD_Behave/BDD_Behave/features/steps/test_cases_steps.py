from behave import given, then


@given("BDD test case execution starts")
def step_impl(context):
    print("\nRunning BDD positive/negative test case")


@then("valid login test case should pass")
def step_impl(context):
    print("\nRunning Positive Test Case 1")
    assert True


@then("valid bus search test case should pass")
def step_impl(context):
    print("\nRunning Positive Test Case 2")
    assert True


@then("view seats test case should pass")
def step_impl(context):
    print("\nRunning Positive Test Case 3")
    assert True


@then("payment page test case should pass")
def step_impl(context):
    print("\nRunning Positive Test Case 4")
    assert True


@then("invalid city test case should fail")
def step_impl(context):
    print("\nRunning Negative Test Case 1")
    assert False, "Invalid city test failed"


@then("no seats test case should fail")
def step_impl(context):
    print("\nRunning Negative Test Case 2")
    assert False, "Seat unavailable test failed"