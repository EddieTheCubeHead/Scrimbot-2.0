# Created by EddieTheCubeHead at 28/12/2021
Feature: Scrim locking and team creation
  # Once a scrim has enough players it can be locked with the 'lock' command
  #
  # After a scrim has been locked the bot should support multiple ways of arranging players into teams with varying
  # degrees of automation
  #
  # Teams can be joined by reacting the team number (works only with games with less than ten teams)
  #   - This functionality is covered in the ScrimReactions.feature file

  @wip
  Scenario: Locking a scrim with enough participants
    Given a Dota 2 scrim with enough players present
    When ;lock is called
    Then command message is deleted
    And embed edited to have fields
      | name                     | value                                               |
      | Author                   | Dota 2 scrim                                        |
      | Icon                     | https://i.imgur.com/OlWIlyY.jpg?1                   |
      | Colour                   | 0xce0000                                            |
      | Status                   | Players locked. Use reactions for manual team selection or the command 'teams _random/balanced/balancedrandom/pickup_' to define teams. |
      | Unassigned               | {{users 1 to 10}}                                   |
      | Spectators               | _empty_                                             |
      | {divider}                | {divider}                                           |
      | Team 1 _(5 more needed)_ | _empty_                                             |
      | Team 2 _(5 more needed)_ | _empty_                                             |
      | Footer                   | React 1️⃣ to join Team 1 or 2️⃣ to join Team 2       |
    And scrim message has reactions
      | reaction | amount |
      | 1️⃣       | 1      |
      | 2️⃣       | 1      |

  Scenario: Attempting to lock a scrim with too few participants
    Given a Dota 2 scrim with 9 players present
    When ;lock is called
    Then command message is deleted
    And error and help received with message
    """
    Could not lock the scrim. Too few participants present.
    """
    And error message deleted after 60 seconds

  Scenario: Attempting to lock a scrim on channel with no scrim
    When ;lock is called
    Then command message is deleted
    And error and help received with message
    """
    Could not find a scrim on channel <#{channel_id}>.
    """

  Scenario: Attempting to lock a scrim that is already locked
    Given a Rocket League scrim with enough players present
    When ;lock is called
    And ;lock is called
    Then command message is deleted
    And embed edited to have fields
      | name                     | value                                         |
      | Author                   | Rocket League scrim                           |
      | Icon                     | https://i.imgur.com/BvQOQyN.png               |
      | Colour                   | 0x0000ff                                      |
      | Status                   | Players locked. Use reactions for manual team selection or the command 'teams _random/balanced/balancedrandom/pickup_' to define teams. |
      | Unassigned               | {{users 1 to 6}}                              |
      | Spectators               | _empty_                                       |
      | {divider}                | {divider}                                     |
      | Team 1 _(3 more needed)_ | _empty_                                       |
      | Team 2 _(3 more needed)_ | _empty_                                       |
      | Footer                   | React 1️⃣ to join Team 1 or 2️⃣ to join Team 2 |
    And error and help received with message
    """
    Could not move a scrim that is waiting for team selection into the state 'waiting for team selection'.
    """
    And error message deleted after 60 seconds

  Scenario: Locking a scrim with participants in queue
    Given a Dota 2 scrim with 15 players present
    When ;lock is called
    Then command message is deleted
    And embed edited to have fields
      | name                     | value                                               |
      | Author                   | Dota 2 scrim                                        |
      | Icon                     | https://i.imgur.com/OlWIlyY.jpg?1                   |
      | Colour                   | 0xce0000                                            |
      | Status                   | Players locked. Use reactions for manual team selection or the command 'teams _random/balanced/balancedrandom/pickup_' to define teams. |
      | Unassigned               | {{users 1 to 10}}                                   |
      | Spectators               | _empty_                                             |
      | {divider}                | {divider}                                           |
      | Team 1 _(5 more needed)_ | _empty_                                             |
      | Team 2 _(5 more needed)_ | _empty_                                             |
      | Footer                   | React 1️⃣ to join Team 1 or 2️⃣ to join Team 2       |
    And scrim message has reactions
      | reaction | amount |
      | 1️⃣       | 1      |
      | 2️⃣       | 1      |

  Scenario: Using the teams command to create random teams
    Given a Dota 2 scrim in locked state
    When ;teams random is called
    Then embed edited to have fields
      | name            | value                                                                                  |
      | Author          | Dota 2 scrim                                                                           |
      | Icon            | https://i.imgur.com/OlWIlyY.jpg?1                                                      |
      | Colour          | 0xce0000                                                                               |
      | Status          | Teams full, use the command 'start' to start the scrim or 'teams clear' to clear teams |
      | Unassigned      | _empty_                                                                                |
      | Spectators      | _empty_                                                                                |
      | {divider}       | {divider}                                                                              |
      | Team 1 _(full)_ | {{5 users in users 1 to 10}}                                                           |
      | Team 2 _(full)_ | {{5 users in users 1 to 10}}                                                           |
      | Footer          | Send command 'start' to start the scrim or send command 'teams clear' to clear teams   |
    And scrim message has no reactions

  Scenario: Using the teams command to clear teams
    Given a Dota 2 scrim with full teams
    When ;teams clear is called
    Then embed edited to have fields
      | name                     | value                                               |
      | Author                   | Dota 2 scrim                                        |
      | Icon                     | https://i.imgur.com/OlWIlyY.jpg?1                   |
      | Colour                   | 0xce0000                                            |
      | Status                   | Players locked. Use reactions for manual team selection or the command 'teams _random/balanced/balancedrandom/pickup_' to define teams. |
      | Unassigned               | {{users 1 to 10}}                                   |
      | Spectators               | _empty_                                             |
      | {divider}                | {divider}                                           |
      | Team 1 _(5 more needed)_ | _empty_                                             |
      | Team 2 _(5 more needed)_ | _empty_                                             |
      | Footer                   | React 1️⃣ to join Team 1 or 2️⃣ to join Team 2       |
    And scrim message has reactions
      | reaction | amount |
      | 1️⃣       | 1      |
      | 2️⃣       | 1      |
