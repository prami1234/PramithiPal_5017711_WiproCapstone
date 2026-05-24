Feature: Ixigo Bus Module Positive and Negative Test Cases

  @positive
  Scenario: TC01 Positive - Valid login test case
    Given BDD test case execution starts
    Then valid login test case should pass

  @positive
  Scenario: TC02 Positive - Valid bus search test case
    Given BDD test case execution starts
    Then valid bus search test case should pass

  @positive
  Scenario: TC03 Positive - View seats test case
    Given BDD test case execution starts
    Then view seats test case should pass

  @positive
  Scenario: TC04 Positive - Payment page test case
    Given BDD test case execution starts
    Then payment page test case should pass

  @negative
  Scenario: TC05 Negative - Invalid city test case
    Given BDD test case execution starts
    Then invalid city test case should be handled

  @negative
  Scenario: TC06 Negative - No seats test case
    Given BDD test case execution starts
    Then no seats test case should be handled