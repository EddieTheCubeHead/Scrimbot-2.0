# Created by EddieTheCubeHead at 28/04/2022
Feature: Setting, updating and displaying user ratings for games
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
  Scenario: Set rating for user with prior results
    Given user has prior Dota 2 results
      | Wins | Losses | Ties | Unregistered |
      | 11   | 8      | 3    | 4            |
    When ;rating {user_1_id} dota 1234 is called
    Then embed received with fields
      | name              | value                             |
      | Author            | Dota 2                            |
      | Icon              | https://i.imgur.com/OlWIlyY.jpg?1 |
      | Colour            | 0xce0000                          |
      | Player statistics | <@!{user_1_id}>                   |
      | Thumbnail         | {user_1_id}.icon                  |
      | Games played      | 26                                |
      | Wins              | 11                                |
      | Losses            | 8                                 |
      | Ties              | 3                                 |
      | Unrecorded        | 4                                 |
      | Rating            | 1234                              |

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

  Scenario: Displaying statistics for an uninitialized user
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

  Scenario: Updating ratings after a game with flat rating change algorithm
    Given user won a FlatRatingChangeGame scrim
    When ;statistics {user_1_id} FlatRatingChangeGame is called
    Then embed received with fields
      | name              | value                                                              |
      | Author            | FlatRatingChangeGame                                               |
      | Icon              | https://cdn.pixabay.com/photo/2012/04/24/12/43/t-39853_960_720.png |
      | Colour            | 0xce0000                                                           |
      | Player statistics | <@!{user_1_id}>                                                    |
      | Thumbnail         | {user_1_id}.icon                                                   |
      | Games played      | 1                                                                  |
      | Wins              | 1                                                                  |
      | Losses            | 0                                                                  |
      | Ties              | 0                                                                  |
      | Unrecorded        | 0                                                                  |
      | Rating            | 1725                                                               |

