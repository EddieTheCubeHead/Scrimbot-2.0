# Created by EddieTheCubeHead at 09/01/2022
Feature: Starting a scrim after team creation
  # When there are no unassigned players left and all teams have at least the minimum amount of players, then the
  # scrim can be started with the 'start' command

  @wip
  Scenario: Calling start on a scrim with full teams
    Given a Dota 2 scrim with full teams
    And all players in voice chat
    When ;start is called
    Then embed received with fields
      | name   | value                                                                                   |
      | Author | Dota 2 scrim                                                                            |
      | Icon   | https://i.imgur.com/OlWIlyY.jpg?1                                                       |
      | Colour | 0xce0000                                                                                |
      | Status | Scrim underway. GLHF!                                                                   |
      | Team 1 | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>{\n}<@{user_4_id}>{\n}<@{user_5_id}>  |
      | Team 2 | <@{user_6_id}>{\n}<@{user_7_id}>{\n}<@{user_8_id}>{\n}<@{user_9_id}>{\n}<@{user_10_id}> |
      | Footer | Declare the result with the command 'winner [team]' or 'tie'                            |
    And scrim message has no reactions