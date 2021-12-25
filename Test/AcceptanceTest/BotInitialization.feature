# Created by EddieTheCubeHead at 05/09/2021
Feature: Bot initialization
  # Bot should be initialized with correct verbose feedback

  @long_test
  Scenario: Add cogs and connect
    Given an uninitialized bot
    When bot is started
    Then cogs are added
    And bot connects
