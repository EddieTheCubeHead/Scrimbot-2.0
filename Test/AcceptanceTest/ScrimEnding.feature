# Created by EddieTheCubeHead at 01/04/2022
Feature: Ending a scrim
  # A scrim can be ended with the 'winner' command or with the 'end' command.
  #
  # 'winner' takes an argument specifying the winner if the scrim when applicable (2 participating teams) or tie while
  # 'end' does not. Thus 'end' does not update any matchmaking ratings.
  #
  # When a scrim with automatic voice switching is ended and a lobby channel for the scrim channel exists, the bot
  # attempts to move all participants into the lobby channel. Any failures in these moving operations are ignored as
  # they are mainly caused by people leaving the server.

  @wip
  Scenario: Ending a scrim with two teams and automatic voice switching by declaring a winner
    Given a Dota 2 scrim with full teams and 2 registered voice channels
    When all players are in voice chat
    And ;start is called
    And ;winner 2 is called
    Then embed edited to have fields
      | name   | value                                                                                   |
      | Author | Dota 2 scrim                                                                            |
      | Icon   | https://i.imgur.com/OlWIlyY.jpg?1                                                       |
      | Colour | 0xce0000                                                                                |
      | Status | Scrim has ended with Team 2 being victorious. Congratulations!                          |
      | Team 1 | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>{\n}<@{user_4_id}>{\n}<@{user_5_id}>  |
      | Team 2 | <@{user_6_id}>{\n}<@{user_7_id}>{\n}<@{user_8_id}>{\n}<@{user_9_id}>{\n}<@{user_10_id}> |
      | Footer | gg wp!                                                                                  |
    And scrim message has no reactions
    And players 1 to 10 moved to lobby voice channel