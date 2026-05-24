Feature: End-to-End Ixigo Bus Booking

  @e2e
  Scenario: Complete bus booking flow till payment page
    Given user launches the browser
    When user opens ixigo homepage
    And user handles the homepage popup
    And user logs in with mobile number
    And user completes otp manually
    Then user should be logged in or login modal should be closed
    When user opens bus section
    And user enters source city
    And user enters destination city
    And user selects travel date
    And user searches buses
    And user applies bus filters
    And user selects seat
    And user continues booking
    And user enters passenger details
    And user proceeds to payment
    Then payment page should open
    And user closes the browser