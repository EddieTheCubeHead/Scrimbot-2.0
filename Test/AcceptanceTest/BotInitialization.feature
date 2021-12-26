# Created by EddieTheCubeHead at 05/09/2021
@no_init
Feature: Bot initialization
  # Bot should be initialized with correct verbose feedback

  @long_test
  Scenario: Add cogs and connect
    When bot is started
    Then cogs are added
    And connection to discord is established successfully
