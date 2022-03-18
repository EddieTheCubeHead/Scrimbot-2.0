# Created by EddieTheCubeHead at 09/01/2022
Feature: Starting a scrim after team creation
  # When there are no unassigned players left and all teams have at least the minimum amount of players, then the
  # scrim can be started with the 'start' command

  @wip
  Scenario: Calling start on a scrim with full teams
    Given a Dota 2 scrim with full teams and 2 registered voice channels
    When all players are in voice chat
    And ;start is called
    Then embed edited to have fields
      | name   | value                                                                                   |
      | Author | Dota 2 scrim                                                                            |
      | Icon   | https://i.imgur.com/OlWIlyY.jpg?1                                                       |
      | Colour | 0xce0000                                                                                |
      | Status | Dota 2 scrim underway. Declare the winner with the command 'winner [team]' or 'tie' or end the scrim without declaring a winner with 'end'. |
      | Team 1 | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>{\n}<@{user_4_id}>{\n}<@{user_5_id}>  |
      | Team 2 | <@{user_6_id}>{\n}<@{user_7_id}>{\n}<@{user_8_id}>{\n}<@{user_9_id}>{\n}<@{user_10_id}> |
      | Footer | gl hf!                                                                                  |
    And scrim message has no reactions
    And players 1 to 5 moved to team 1 voice channel
    And players 6 to 10 moved to team 2 voice channel