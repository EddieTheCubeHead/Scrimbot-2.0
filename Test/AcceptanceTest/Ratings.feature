# Created by EddieTheCubeHead at 28/04/2022
Feature: Setting, updating and displaying user ratings for games on both guild and global basis
  # Guild admins can set and update user ratings with the command 'rating'
  #  - Usage: rating [user] [game] [value]

  @as_admin
  Scenario: Set rating for existing user in existing game with acceptable value
    When ;rating {user_id} dota 2187 is called
    Then embed received with fields
      | name              | value                             |
      | Author            | Dota 2                            |
      | Icon              | https://i.imgur.com/OlWIlyY.jpg?1 |
      | Colour            | 0xce0000                          |
      | Player statistics | <@!{user_id}>                     |
      | Thumbnail         | {user_id}.icon                    |
      | Games played      | 0                                 |
      | Wins              | 0                                 |
      | Losses            | 0                                 |
      | Ties              | 0                                 |
      | Unrecorded        | 0                                 |
      | Rating            | 2187                              |

  Scenario: Attempting to set rating without moderator level rights
    When ;rating {user_id} dota 2187 is called
    Then error and help received with message
    """
    Using command 'rating' requires at least admin level rights for this guild. (Your permission level: member)
    """

  @as_admin
  Scenario: Reset rating for existing user in existing game with acceptable value
    When ;rating {user_id} dota 2187 is called
    And ;rating {user_id} dota 1008 is called
    Then embed received with fields
      | name              | value                             |
      | Author            | Dota 2                            |
      | Icon              | https://i.imgur.com/OlWIlyY.jpg?1 |
      | Colour            | 0xce0000                          |
      | Player statistics | <@!{user_id}>                     |
      | Thumbnail         | {user_id}.icon                    |
      | Games played      | 0                                 |
      | Wins              | 0                                 |
      | Losses            | 0                                 |
      | Ties              | 0                                 |
      | Unrecorded        | 0                                 |
      | Rating            | 2187                              |
    And embed received with fields
      | name              | value                             |
      | Author            | Dota 2                            |
      | Icon              | https://i.imgur.com/OlWIlyY.jpg?1 |
      | Colour            | 0xce0000                          |
      | Player statistics | <@!{user_id}>                     |
      | Thumbnail         | {user_id}.icon                    |
      | Games played      | 0                                 |
      | Wins              | 0                                 |
      | Losses            | 0                                 |
      | Ties              | 0                                 |
      | Unrecorded        | 0                                 |
      | Rating            | 1008                              |

  @as_admin
  Scenario: Attempting to set rating for existing user in existing game with too low value
    When ;rating {user_id} csgo 5001 is called
    Then error and help received with message
    """
    Could not convert argument '5001' into type user rating because rating is not between 0 and 5000
    """

  @as_admin
  Scenario: Attempting to set rating for existing user in existing game with too low value
    When ;rating {user_id} csgo -1 is called
    Then error and help received with message
    """
    Could not convert argument '-1' into type user rating because rating is not between 0 and 5000
    """

  @as_admin
  Scenario: Attempting to set rating for existing user in existing game with string value
    When ;rating {user_id} csgo invalid is called
    Then error and help received with message
    """
    Could not convert argument 'invalid' into type user rating because argument is not a whole number
    """

  @as_admin
  Scenario: Attempting to set rating for invalid user
    When ;rating {invalid_id} dota 1000 is called
    Then error and help received with message
    """
    Could not convert argument '-1' into type User because argument is not a valid username, nickname, user id or mention on this server
    """

  @as_admin
  Scenario: Attempting to set rating for invalid game
    When ;rating {user_id} invalid 1000 is called
    Then error and help received with message
    """
    Could not convert argument 'invalid' into type Game because argument did not correspond to any name or alias for a registered game
    """

  Scenario: Displaying statistics for uninitialized user
    When ;statistics {user_id} dota is called
    Then embed received with fields
      | name              | value                             |
      | Author            | Dota 2                            |
      | Icon              | https://i.imgur.com/OlWIlyY.jpg?1 |
      | Colour            | 0xce0000                          |
      | Player statistics | <@!{user_id}>                     |
      | Thumbnail         | {user_id}.icon                    |
      | Games played      | 0                                 |
      | Wins              | 0                                 |
      | Losses            | 0                                 |
      | Ties              | 0                                 |
      | Unrecorded        | 0                                 |
      | Rating            | 1700                              |

  Scenario: Displaying statistics for an initialized user
    Given user {user_id} has a dota rating of 400
    When ;statistics {user_id} dota is called
    Then embed received with fields
      | name              | value                             |
      | Author            | Dota 2                            |
      | Icon              | https://i.imgur.com/OlWIlyY.jpg?1 |
      | Colour            | 0xce0000                          |
      | Player statistics | <@!{user_id}>                     |
      | Thumbnail         | {user_id}.icon                    |
      | Games played      | 0                                 |
      | Wins              | 0                                 |
      | Losses            | 0                                 |
      | Ties              | 0                                 |
      | Unrecorded        | 0                                 |
      | Rating            | 400                               |
