# Created by EddieTheCubeHead at 13/04/2022
Feature: Terminating a scrim
  # A scrim can be forcefully terminated with 'terminate' during any state of the scrim. This will not update
  # matchmaking ratings or save the scrim to database.

  Scenario: Terminating a scrim during looking for players phase
    Given a Valorant scrim
    When ;terminate is called
    Then embed edited to have fields
      | name   | value                                                                     |
      | Author | Valorant scrim                                                            |
      | Icon   | https://www.citypng.com/public/uploads/preview/-41603132788rzosdsitdt.png |
      | Colour | 0xeb4034                                                                  |
      | Status | Scrim terminated manually by <@{user_id}>                                 |
      | Footer | f                                                                         |
    And scrim message has no reactions

  Scenario: Terminating a scrim during locked phase
    Given an Valorant scrim in locked state
    When ;terminate is called
    Then embed edited to have fields
      | name   | value                                                                     |
      | Author | Valorant scrim                                                            |
      | Icon   | https://www.citypng.com/public/uploads/preview/-41603132788rzosdsitdt.png |
      | Colour | 0xeb4034                                                                  |
      | Status | Scrim terminated manually by <@{user_id}>                                 |
      | Footer | f                                                                         |
    And scrim message has no reactions

  Scenario: Terminating a scrim during waiting for voice phase
    Given a Valorant scrim with full teams and 2 registered voice channels
    When players 1 to 9 are in voice chat
    And player 10 is not in voice chat
    And ;start is called
    Then embed edited to have fields
      | name   | value                                                                     |
      | Author | Valorant scrim                                                            |
      | Icon   | https://www.citypng.com/public/uploads/preview/-41603132788rzosdsitdt.png |
      | Colour | 0xeb4034                                                                  |
      | Status | Starting Valorant scrim. Waiting for all players to join voice chat...    |
      | Team 1 | {{users 1 to 5}}                                                          |
      | Team 2 | {{users 6 to 10}}                                                         |
      | Footer | Scrim will start automatically when all players are in voice chat         |
    When ;terminate is called
    Then embed edited to have fields
      | name   | value                                                                     |
      | Author | Valorant scrim                                                            |
      | Icon   | https://www.citypng.com/public/uploads/preview/-41603132788rzosdsitdt.png |
      | Colour | 0xeb4034                                                                  |
      | Status | Scrim terminated manually by <@{user_id}>                                 |
      | Footer | f                                                                         |
    And scrim message has no reactions

  Scenario: Terminating a scrim during started phase
    Given a Valorant scrim with full teams and 2 registered voice channels
    When ;start false is called
    Then embed edited to have fields
      | name   | value                                                                     |
      | Author | Valorant scrim                                                            |
      | Icon   | https://www.citypng.com/public/uploads/preview/-41603132788rzosdsitdt.png |
      | Colour | 0xeb4034                                                                  |
      | Status | Valorant scrim underway. Declare the winner with the command 'winner [team]' or 'tie' or end the scrim without declaring a winner with 'end'. |
      | Team 1 | {{users 1 to 5}}                                                          |
      | Team 2 | {{users 6 to 10}}                                                         |
      | Footer | gl hf!                                                                    |
    When ;terminate is called
    Then embed edited to have fields
      | name   | value                                                                     |
      | Author | Valorant scrim                                                            |
      | Icon   | https://www.citypng.com/public/uploads/preview/-41603132788rzosdsitdt.png |
      | Colour | 0xeb4034                                                                  |
      | Status | Scrim terminated manually by <@{user_id}>                                 |
      | Footer | f                                                                         |
    And scrim message has no reactions