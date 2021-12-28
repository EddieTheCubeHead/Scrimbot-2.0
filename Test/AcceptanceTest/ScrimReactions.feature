# Created by EddieTheCubeHead at 17/12/2021
Feature: Scrim and scrim team leaving/joining with reactions

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

  @wip
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
