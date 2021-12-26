# Created by EddieTheCubeHead at 27/12/2021
Feature: Channel registration rewrite
  # Bot should be able to register channels to be used as scrim setup/voice channels
  # Channel registration can be done without arguments
  #  - This creates a scrim capable text channel with no associated voice channels
  # Successful channel registration should always have a formatted embed as feedback
  #  - The embed is named "New scrim channel registered successfully" and contains fields for all registered channels
  #  - All channel fields have channel usage (text channel/voice lobby/team n channel) and mention the channel
  # Channel registration can be done by manually giving channels for voice channels
  #  - Channel mentions happen with discord converter format (name/mention/id)
  #  - Team channels are registered in order, lobby channel is indicated with "l:"-prefix
  # Channel registration can be done automatically from a channel group by giving single argument "auto"
  #  - If the group has 3 or more voice channels, channel teams/lobby status is parsed from channel name
  #  - Channels for teams are expected to have team numbers in name and follow otherwise identical format
  #  - If there is exactly one channel that doesn't follow the format, that channel is assigned as the lobby channel
  #  - If there are exactly 2 voice channels in the group, they are assigned to teams 1 and 2 respectively
  #  - If there is exactly 1 voice channel in the group, it is assigned as lobby channel
  # If text channel or voice channel is already registered for another scrim this is communicated through an exception
  #  - This exception is displayed in an embed like the rest of exceptions of the bot

  Scenario: Registering a channel with no voice channels
    When ;register is called
    Then channel registered
    And embed received with fields
      | name                                       | value           |
      | New scrim channel registered successfully! | Channel data:   |
      | Text channel                               | <#{channel_id}> |

  Scenario: Registering a channel that is already registered
    When ;register is called
    And ;register is called
    Then embed received with fields
      | name                                       | value           |
      | New scrim channel registered successfully! | Channel data:   |
      | Text channel                               | <#{channel_id}> |
    And error and help received with message
      """
      Text channel <#{channel_id}> is already registered for scrim usage.
      """

  Scenario: Registering a channel with a lobby channel and two team voice channels
    Given exists 3 voice channels
    When ;register l:{voice_1_id} {voice_2_id} {voice_3_id} is called
    Then embed received with fields
      | name                                       | value           |
      | New scrim channel registered successfully! | Channel data:   |
      | Text channel                               | <#{channel_id}> |
      | Voice lobby                                | <#{voice_1_id}> |
      | Team 1 voice                               | <#{voice_2_id}> |
      | Team 2 voice                               | <#{voice_3_id}> |

  Scenario: Registering a channel with a reserved voice channel
    Given exists 3 voice channels
    When ;register {voice_1_id} {voice_2_id} is called
    And ;register {voice_2_id} {voice_3_id} is called from another channel
    Then embed received with fields
      | name                                       | value           |
      | New scrim channel registered successfully! | Channel data:   |
      | Text channel                               | <#{channel_id}> |
      | Team 1 voice                               | <#{voice_1_id}> |
      | Team 2 voice                               | <#{voice_2_id}> |
    And error and help received with message
      """
      Voice channel <#{voice_2_id}> is already associated with scrim channel <#{channel_id}>.
      """

  Scenario: Registering a channel in a group with automatic voice channel detection, lobby channel and two team channels
    Given exists channel group
      | channel type | channel name |
      | text         | scrim-1      |
      | voice        | Lobby        |
      | voice        | Team 1       |
      | voice        | Team 2       |
    When ;register auto is called
    Then embed received with fields
      | name                                       | value           |
      | New scrim channel registered successfully! | Channel data:   |
      | Text channel                               | <#{channel_id}> |
      | Voice lobby                                | <#{voice_1_id}> |
      | Team 1 voice                               | <#{voice_2_id}> |
      | Team 2 voice                               | <#{voice_3_id}> |

  Scenario: Registering a channel in a group with automatic voice channel detection and two channels
    Given exists channel group
      | channel type | channel name |
      | text         | scrim-1      |
      | voice        | Radiant      |
      | voice        | Dire         |
    When ;register auto is called
    Then embed received with fields
      | name                                       | value           |
      | New scrim channel registered successfully! | Channel data:   |
      | Text channel                               | <#{channel_id}> |
      | Team 1 voice                               | <#{voice_1_id}> |
      | Team 2 voice                               | <#{voice_2_id}> |

  Scenario: Registering a channel in a group with automatic voice channel detection and one channel
    Given exists channel group
      | channel type | channel name |
      | text         | scrim-1      |
      | voice        | Scrimmage    |
    When ;register auto is called
    Then embed received with fields
      | name                                       | value           |
      | New scrim channel registered successfully! | Channel data:   |
      | Text channel                               | <#{channel_id}> |
      | Voice lobby                                | <#{voice_1_id}> |
