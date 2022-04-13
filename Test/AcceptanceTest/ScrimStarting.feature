# Created by EddieTheCubeHead at 09/01/2022
Feature: Starting a scrim after team creation
  # When there are no unassigned players left and all teams have at least the minimum amount of players, then the
  # scrim can be started with the 'start' command. Given no arguments the command attempts moving players into voice
  # channels registered for the scrim channel, if such exist. If this is not possible, the scrim moves into a state
  # where it waits for players to move into voice channels and starts automatically when all players are in voice
  # channels in the scrim guild.
  #
  # 'start' can be given a boolean argument to specify whether to move players into voice channels. If given false
  # player moving stage of the process is skipped.
  #
  # If scrim waits for more than five minutes for players to join voice chat then state is reverted to team creation

  Scenario: Starting a scrim with full teams with automatic voice channel moving
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

  Scenario: Starting a scrim with fewer voice channels than teams
    Given a Dota 2 scrim with full teams and 1 registered voice channel
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
    And no players moved

  Scenario: Starting a scrim with full teams with automatic voice channel moving disabled
    Given a Dota 2 scrim with full teams and 2 registered voice channel
    When all players are in voice chat
    And ;start false is called
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
    And no players moved

  Scenario: Starting a scrim with full teams and automatic voice channel moving when one player is not in voice
    Given a Dota 2 scrim with full teams and 2 registered voice channels
    When players 1 to 9 are in voice chat
    And player 10 is not in voice chat
    And ;start is called
    Then embed edited to have fields
      | name   | value                                                                                   |
      | Author | Dota 2 scrim                                                                            |
      | Icon   | https://i.imgur.com/OlWIlyY.jpg?1                                                       |
      | Colour | 0xce0000                                                                                |
      | Status | Starting Dota 2 scrim. Waiting for all players to join voice chat...                    |
      | Team 1 | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>{\n}<@{user_4_id}>{\n}<@{user_5_id}>  |
      | Team 2 | <@{user_6_id}>{\n}<@{user_7_id}>{\n}<@{user_8_id}>{\n}<@{user_9_id}>{\n}<@{user_10_id}> |
      | Footer | Scrim will start automatically when all players are in voice chat                       |
    And scrim message has reactions
      | reaction | amount |
      | 1️⃣       | 6      |
      | 2️⃣       | 6      |
    When player 10 connects to voice
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

  Scenario: Starting a scrim with full teams and automatic voice channel moving when multiple players are not in voice
    Given a Dota 2 scrim with full teams and 2 registered voice channels
    When players 1 to 4 are in voice chat
    And players 6 to 9 are in voice chat
    And players 5 and 10 are not in voice chat
    And ;start is called
    Then embed edited to have fields
      | name   | value                                                                                   |
      | Author | Dota 2 scrim                                                                            |
      | Icon   | https://i.imgur.com/OlWIlyY.jpg?1                                                       |
      | Colour | 0xce0000                                                                                |
      | Status | Starting Dota 2 scrim. Waiting for all players to join voice chat...                    |
      | Team 1 | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>{\n}<@{user_4_id}>{\n}<@{user_5_id}>  |
      | Team 2 | <@{user_6_id}>{\n}<@{user_7_id}>{\n}<@{user_8_id}>{\n}<@{user_9_id}>{\n}<@{user_10_id}> |
      | Footer | Scrim will start automatically when all players are in voice chat                       |
    And scrim message has reactions
      | reaction | amount |
      | 1️⃣       | 6      |
      | 2️⃣       | 6      |
    When player 10 connects to voice
    Then embed edited to have fields
      | name   | value                                                                                   |
      | Author | Dota 2 scrim                                                                            |
      | Icon   | https://i.imgur.com/OlWIlyY.jpg?1                                                       |
      | Colour | 0xce0000                                                                                |
      | Status | Starting Dota 2 scrim. Waiting for all players to join voice chat...                    |
      | Team 1 | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>{\n}<@{user_4_id}>{\n}<@{user_5_id}>  |
      | Team 2 | <@{user_6_id}>{\n}<@{user_7_id}>{\n}<@{user_8_id}>{\n}<@{user_9_id}>{\n}<@{user_10_id}> |
      | Footer | Scrim will start automatically when all players are in voice chat                       |
    And scrim message has reactions
      | reaction | amount |
      | 1️⃣       | 6      |
      | 2️⃣       | 6      |
    When player 5 connects to voice
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

  Scenario: Attempting to start a scrim but players don't join voice channel in five minutes
    Given a Dota 2 scrim with full teams and 2 registered voice channels
    When players 1 to 9 are in voice chat
    And player 10 is not in voice chat
    And ;start is called
    And 5 minutes elapses
    And the task to prune waiting scrims is ran
    Then embed edited to have fields
      | name                     | value                                         |
      | Author                   | Dota 2 scrim                                  |
      | Icon                     | https://i.imgur.com/OlWIlyY.jpg?1             |
      | Colour                   | 0xce0000                                      |
      | Status                   | Teams full, use the command 'start' to start the scrim or 'teams clear' to clear teams |
      | Unassigned               | _empty_                                       |
      | Spectators               | _empty_                                       |
      | {divider}                | {divider}                                     |
      | Team 1 _(full)_          | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>{\n}<@{user_4_id}>{\n}<@{user_5_id}>  |
      | Team 2 _(full)_          | <@{user_6_id}>{\n}<@{user_7_id}>{\n}<@{user_8_id}>{\n}<@{user_9_id}>{\n}<@{user_10_id}> |
      | Footer                   | Send command 'start' to start the scrim or send command 'teams clear' to clear teams |
    And scrim message has reactions
      | reaction | amount |
      | 1️⃣       | 6      |
      | 2️⃣       | 6      |