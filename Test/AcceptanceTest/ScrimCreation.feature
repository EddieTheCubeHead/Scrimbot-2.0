# Created by EddieTheCubeHead at 26/11/2021
Feature: Scrim creation
  # Users can create scrims of supported games

  Scenario: Basic scrim creation
    Given an initialized bot
    And channel '23' registered for scrims in guild '1'
    When ';scrim dota' is called with
      | user | channel | guild |
      | 1    | 23      | 1     |
    Then embed received with fields
      | name         | value                                               |
      | Author       | Dota 2 scrim                                        |
      | Icon         | https://i.imgur.com/OlWIlyY.jpg?1                   |
      | Colour       | 0xce0000                                            |
      | Status       | Looking for players, 10 more required.              |
      | Participants | __empty__                                           |
      | Spectators   | __empty__                                           |
      | Footer       | To join players react 🎮 To join spectators react 👁 |