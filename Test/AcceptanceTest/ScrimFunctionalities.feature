# Created by EddieTheCubeHead at 05/09/2021
Feature: ScrimFunctionalities
  # Bot should be able to register channels to be used as scrim setup/voice channels
  # Bot should be able to setup scrim signup forms on scrim setup channels
  # Bot should offer players a chance to sign in to a sign as a player or spectator via discord reactions
  # Bot should recognize when a scrim has enough players based on the game and lock current participants
  # Bot should support players choosing their teams via reactions
  # Bot should recognize when all teams have enough players and all participants are in a team and let players start
  #   the scrim. This should move all players to assigned voice channels by default if enough channels exist
  # Bot should offer a way to start a scrim without moving the players
  # Bot should let the players declare a winning team for the scrim
  # In scrims with more than 2 teams the bot should support listing the result of the scrim in descending order
  #   (Winner - 2nd place - 3rd place - etc.)
  # Bot should support terminating scrims by users with global bot admin rights, server bot admin rights or scrim owner
  # Bot should always update the embed message to reflect the state of the scrim

  Scenario: Registering a channel with no voice channels
    Given an initialized bot
    When ';register' is called with
      | user | channel | guild |
      | 1    | 1       | 1     |
    Then channel '1' registered
    And embed received with fields
      | name                                       | value         |
      | New scrim channel registered successfully! | Channel data: |
      | Text channel                               | <#1>          |

  Scenario: Registering a channel with a lobby channel and two team voice channels
    Given an initialized bot
    And exists discord voice channels
      | guild | channel |
      | 1     | 3       |
      | 1     | 4       |
      | 1     | 5       |
    When ';register l:3 4 5' is called with
      | user | channel | guild |
      | 1    | 2       | 1     |
    Then embed received with fields
      | name                                       | value         |
      | New scrim channel registered successfully! | Channel data: |
      | Text channel                               | <#2>          |
      | Voice lobby                                | <#3>          |
      | Team 1 voice                               | <#4>          |
      | Team 2 voice                               | <#5>          |

  Scenario: Registering a channel in a group with automatic voice channel detection
    Given an initialized bot
    And exists channel group '6' in guild '2'
      | channel type | channel name | channel id |
      | text         | scrim-1      | 7          |
      | voice        | Lobby        | 8          |
      | voice        | Team 1       | 9          |
      | voice        | Team 2       | 10         |
    When ';register auto' is called with
      | user | channel | guild |
      | 1    | 7       | 2     |
    Then embed received with fields
      | name                                       | value         |
      | New scrim channel registered successfully! | Channel data: |
      | Text channel                               | <#7>          |
      | Voice lobby                                | <#8>          |
      | Team 1 voice                               | <#9>          |
      | Team 2 voice                               | <#10>         |
