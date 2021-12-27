# Created by EddieTheCubeHead at 17/12/2021
Feature: Scrim and scrim team leaving/joining with reactions

  Scenario: Joining a scrim with reactions
    Given a Dota 2 scrim
    When a user reacts with 🎮
    Then embed edited to have fields
      | name         | value                                               |
      | Author       | Dota 2 scrim                                        |
      | Icon         | https://i.imgur.com/OlWIlyY.jpg?1                   |
      | Colour       | 0xce0000                                            |
      | Status       | Looking for players, 9 more required.               |
      | Participants | <#{user_1_id}>                                      |
      | Spectators   | _empty_                                             |
      | Footer       | To join players react 🎮 To join spectators react 👁 |

  Scenario: Multiple users joining with a reaction
    Given a Dota 2 scrim
    When 3 users react with 🎮
    Then embed edited to have fields
      | name         | value                                               |
      | Author       | Dota 2 scrim                                        |
      | Icon         | https://i.imgur.com/OlWIlyY.jpg?1                   |
      | Colour       | 0xce0000                                            |
      | Status       | Looking for players, 7 more required.               |
      | Participants | <#{user_1_id}>{\n}<#{user_2_id}>{\n}<#{user_3_id}>  |
      | Spectators   | _empty_                                             |
      | Footer       | To join players react 🎮 To join spectators react 👁 |