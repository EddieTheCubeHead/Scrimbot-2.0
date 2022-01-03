# Created by EddieTheCubeHead at 17/12/2021
Feature: Scrim and scrim team leaving/joining with reactions
  # Users can join and leave teams by adding reactions: effect depends on scrim phase

  # In Looking For Players phase, reactions 🎮 and 👁 can be used to join players and spectators respectively
  #   - If user is not in either and participants is not full the user should be added to the corresponding group
  #   - If participants are full joining participants should put the user into the queue
  #   - If user is already a participant/spectator they cannot join the other group
  #     - If this happens, the reaction that was used for invalid joining should be deleted
  #   - Removing the reaction used to join a group will remove the user from the group

  Scenario: User joining participants by adding a reaction
    Given a Dota 2 scrim
    When a user reacts with 🎮
    Then embed edited to have fields
      | name         | value                                               |
      | Author       | Dota 2 scrim                                        |
      | Icon         | https://i.imgur.com/OlWIlyY.jpg?1                   |
      | Colour       | 0xce0000                                            |
      | Status       | Looking for players, 9 more required.               |
      | Participants | <@{user_1_id}>                                      |
      | Spectators   | _empty_                                             |
      | Footer       | To join players react 🎮 To join spectators react 👁 |
    And scrim message has reactions
      | reaction | amount |
      | 🎮       | 2      |
      | 👁       | 1      |

  Scenario: Multiple users joining participants by adding a reaction
    Given a Dota 2 scrim
    When 3 users react with 🎮
    Then embed edited to have fields
      | name         | value                                               |
      | Author       | Dota 2 scrim                                        |
      | Icon         | https://i.imgur.com/OlWIlyY.jpg?1                   |
      | Colour       | 0xce0000                                            |
      | Status       | Looking for players, 7 more required.               |
      | Participants | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>  |
      | Spectators   | _empty_                                             |
      | Footer       | To join players react 🎮 To join spectators react 👁 |
    And scrim message has reactions
      | reaction | amount |
      | 🎮       | 4      |
      | 👁       | 1      |

  Scenario: User joining spectators by adding a reaction
    Given a Dota 2 scrim
    When a user reacts with 👁
    Then embed edited to have fields
      | name         | value                                               |
      | Author       | Dota 2 scrim                                        |
      | Icon         | https://i.imgur.com/OlWIlyY.jpg?1                   |
      | Colour       | 0xce0000                                            |
      | Status       | Looking for players, 10 more required.              |
      | Participants | _empty_                                             |
      | Spectators   | <@{user_1_id}>                                      |
      | Footer       | To join players react 🎮 To join spectators react 👁 |
    And scrim message has reactions
      | reaction | amount |
      | 🎮       | 1      |
      | 👁       | 2      |

  Scenario: Multiple users joining spectators by adding a reaction
    Given a Dota 2 scrim
    When 3 users react with 👁
    Then embed edited to have fields
      | name         | value                                               |
      | Author       | Dota 2 scrim                                        |
      | Icon         | https://i.imgur.com/OlWIlyY.jpg?1                   |
      | Colour       | 0xce0000                                            |
      | Status       | Looking for players, 10 more required.              |
      | Participants | _empty_                                             |
      | Spectators   | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>  |
      | Footer       | To join players react 🎮 To join spectators react 👁 |
    And scrim message has reactions
      | reaction | amount |
      | 🎮       | 1      |
      | 👁       | 4      |

  Scenario: Participant leaves by removing their reaction
    Given a Rocket League scrim
    When 2 users react with 🎮
    And user 2 removes reaction 🎮
    Then embed edited to have fields
      | name         | value                                               |
      | Author       | Rocket League scrim                                 |
      | Icon         | https://i.imgur.com/BvQOQyN.png                     |
      | Colour       | 0x0000ff                                            |
      | Status       | Looking for players, 5 more required.               |
      | Participants | <@{user_1_id}>                                      |
      | Spectators   | _empty_                                             |
      | Footer       | To join players react 🎮 To join spectators react 👁 |
    And scrim message has reactions
      | reaction | amount |
      | 🎮       | 2      |
      | 👁       | 1      |

  Scenario: Spectator leaves by removing their reaction
    Given a Rocket League scrim
    When 2 users react with 👁
    And user 2 removes reaction 👁
    Then embed edited to have fields
      | name         | value                                               |
      | Author       | Rocket League scrim                                 |
      | Icon         | https://i.imgur.com/BvQOQyN.png                     |
      | Colour       | 0x0000ff                                            |
      | Status       | Looking for players, 6 more required.               |
      | Participants | _empty_                                             |
      | Spectators   | <@{user_1_id}>                                      |
      | Footer       | To join players react 🎮 To join spectators react 👁 |
    And scrim message has reactions
      | reaction | amount |
      | 🎮       | 1      |
      | 👁       | 2      |

  Scenario: Scrim with concrete player count filled gives locking info
    Given a Rocket League scrim
    When 6 users react with 🎮
    Then embed edited to have fields
      | name         | value                                                                                     |
      | Author       | Rocket League scrim                                                                       |
      | Icon         | https://i.imgur.com/BvQOQyN.png                                                           |
      | Colour       | 0x0000ff                                                                                  |
      | Status       | All players present. Send command 'lock' to start team selection.                         |
      | Participants | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>{\n}<@{user_4_id}>{\n}<@{user_5_id}>{\n}<@{user_6_id}> |
      | Spectators   | _empty_                                                                                   |
      | Footer       | To join players react 🎮 To join spectators react 👁 To lock the teams send command 'lock' |
    And scrim message has reactions
      | reaction | amount |
      | 🎮       | 7      |
      | 👁       | 1      |

  Scenario: Scrim filled and new players put into the queue
    Given a Rocket League scrim
    When 8 users react with 🎮
    Then embed edited to have fields
      | name         | value                                                                                     |
      | Author       | Rocket League scrim                                                                       |
      | Icon         | https://i.imgur.com/BvQOQyN.png                                                           |
      | Colour       | 0x0000ff                                                                                  |
      | Status       | All players present. Send command 'lock' to start team selection.                         |
      | Participants | <@{user_1_id}>{\n}<@{user_2_id}>{\n}<@{user_3_id}>{\n}<@{user_4_id}>{\n}<@{user_5_id}>{\n}<@{user_6_id}> |
      | Spectators   | _empty_                                                                                   |
      | Queue        | <@{user_7_id}>{\n}<@{user_8_id}>                                                          |
      | Footer       | To join players react 🎮 To join spectators react 👁 To lock the teams send command 'lock' |
    And scrim message has reactions
      | reaction | amount |
      | 🎮       | 9      |
      | 👁       | 1      |

  Scenario: Attempting to join spectators after participants
    Given an Among Us scrim
    When a user reacts with 🎮
    And user 1 reacts with 👁
    Then embed edited to have fields
      | name         | value                                                                     |
      | Author       | Among Us scrim                                                            |
      | Icon         | https://www.scarsdalelibrary.org/sites/default/files/2021-02/among_us.jpg |
      | Colour       | 0xff0000                                                                  |
      | Status       | Looking for players, 5 more required.                                     |
      | Participants | <@{user_1_id}>                                                            |
      | Spectators   | _empty_                                                                   |
      | Footer       | To join players react 🎮 To join spectators react 👁                       |
    And scrim message has reactions
      | reaction | amount |
      | 🎮       | 2      |
      | 👁       | 1      |

  Scenario: Attempting to join participants after spectators
    Given an Among Us scrim
    When a user reacts with 👁
    And user 1 reacts with 🎮
    Then embed edited to have fields
      | name         | value                                                                     |
      | Author       | Among Us scrim                                                            |
      | Icon         | https://www.scarsdalelibrary.org/sites/default/files/2021-02/among_us.jpg |
      | Colour       | 0xff0000                                                                  |
      | Status       | Looking for players, 6 more required.                                     |
      | Participants | _empty_                                                                   |
      | Spectators   | <@{user_1_id}>                                                            |
      | Footer       | To join players react 🎮 To join spectators react 👁                       |
    And scrim message has reactions
      | reaction | amount |
      | 🎮       | 1      |
      | 👁       | 2      |

    @wip
    Scenario: Joining a team in a locked scrim
      Given a Dota 2 scrim in locked state
      When user 1 reacts with 1️⃣
      Then embed edited to have fields
        | name                     | value                                               |
        | Author                   | Dota 2 scrim                                        |
        | Icon                     | https://i.imgur.com/OlWIlyY.jpg?1                   |
        | Colour                   | 0xce0000                                            |
        | Status                   | Players locked. Use reactions for manual team selection or the command 'teams _random/balanced/balancedrandom/pickup_' to define teams. |
        | Unassigned               | <@{user_2_id}>{\n}<@{user_3_id}>{\n}<@{user_4_id}>{\n}<@{user_5_id}>{\n}<@{user_6_id}>{\n}<@{user_7_id}>{\n}<@{user_8_id}>{\n}<@{user_9_id}>{\n}<@{user_10_id}> |
        | Spectators               | _empty_                                             |
        | {divider}                | {divider}                                           |
        | Team 1 _(4 more needed)_ | <@{user_1_id}>                                      |
        | Team 2 _(5 more needed)_ | _empty_                                             |
        | Footer                   | React 1️⃣ to join Team 1 or 2️⃣ to join Team 2       |
      And scrim message has reactions
        | reaction | amount |
        | 1️⃣       | 2      |
        | 2️⃣       | 1      |
