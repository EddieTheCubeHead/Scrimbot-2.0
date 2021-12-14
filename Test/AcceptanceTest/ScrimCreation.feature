# Created by EddieTheCubeHead at 26/11/2021
Feature: Scrim creation
  # Users can create scrims of supported games
  #   - If the channel that scrim is trying to be created on is not registered for scrims a warning is given

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
      | Participants | _empty_                                             |
      | Spectators   | _empty_                                             |
      | Footer       | To join players react 🎮 To join spectators react 👁 |
    And team joining emojis reacted by bot

  Scenario: Trying to create a scrim on an unregistered channel
    Given an initialized bot
    When ';scrim cs' is called with
      | user | channel | guild |
      | 1    | 24      | 4     |
    Then error and help received with message 'Cannot create a scrim on channel <\#24> because it is not registered for scrim usage.'