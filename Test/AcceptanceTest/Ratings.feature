# Created by EddieTheCubeHead at 28/04/2022
Feature: Setting, updating and displaying user ratings for games on both guild and global basis
  # Guild moderators and admins can set and update user ratings with the command 'rating'
  #  - Usage: rating [user] [game] [value]
  #
  # Has a variant for global ratings (guild id = 0)
  #  - Usage: globalrating [user] [game] [value]

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