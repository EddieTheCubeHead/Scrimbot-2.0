# Created by EddieTheCubeHead at 05/09/2021
Feature: Channel registration
  # Bot should be able to register channels to be used as scrim setup/voice channels
  # Channel registration can be done without arguments
  #  - This creates a scrim capable text channel with no associated voice channels
  # Successful channel registration should always have a formatted embed as feedback
  #  - The embed is named "New scrim channel registered successfully" and contains fields for all registered channels
  #  - All channel fields have channel usage (text channe/voice lobby/team n channel) and mention the channel
  # Channel registration can be done by manually giving channels for voice channels
  #  - Channel mentions happen with discord converter format (name/mention/id)
  #  - Team channels are registered in order, lobby channel is indicated with "l:"-prefix
  # Channel registration can be done automatically from a channel group by giving single argument "auto"
  #  - If the group has 3 or more voice channels, channel teams/lobby status is parsed from channel name
  #  - Channels for teams are expected to have team numbers in name and follow otherwise identical format
  #  - If there is exactly one channel that doesn't follow the format, that channel is assigned as the lobby channel
  #  - If there are exactly 2 voice channels in the group, they are assigned to teams 1 and 2 respectively
  #  - If there is exactly 1 voice channel in the group, it is assigned as lobby channel

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

  Scenario: Registering a channel that is already registered
    Given an initialized bot
    When ';register' is called with
      | user | channel | guild |
      | 1    | 18      | 5     |
    And ';register' is called with
      | user | channel | guild |
      | 1    | 18      | 5     |
    Then embed received with fields
      | name                                       | value         |
      | New scrim channel registered successfully! | Channel data: |
      | Text channel                               | <#18>         |
    And error and help received with messages 'Text channel <\#18> is already registered for scrim usage.' and ';register'

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

  Scenario: Registering a channel in a group with automatic voice channel detection, lobby channel and two team channels
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

  Scenario: Registering a channel in a group with automatic voice channel detection and two channels
    Given an initialized bot
    And exists channel group '14' in guild '3'
      | channel type | channel name | channel id |
      | text         | scrim-1      | 11         |
      | voice        | Radiant      | 12         |
      | voice        | Dire         | 13         |
    When ';register auto' is called with
      | user | channel | guild |
      | 1    | 11      | 3     |
    Then embed received with fields
      | name                                       | value         |
      | New scrim channel registered successfully! | Channel data: |
      | Text channel                               | <#11>         |
      | Team 1 voice                               | <#12>         |
      | Team 2 voice                               | <#13>         |

  Scenario: Registering a channel in a group with automatic voice channel detection and one channel
    Given an initialized bot
    And exists channel group '15' in guild '1'
      | channel type | channel name | channel id |
      | text         | scrim-1      | 16         |
      | voice        | Scrimmage    | 17         |
    When ';register auto' is called with
      | user | channel | guild |
      | 5    | 16      | 1     |
    Then embed received with fields
      | name                                       | value         |
      | New scrim channel registered successfully! | Channel data: |
      | Text channel                               | <#16>         |
      | Voice lobby                                | <#17>         |
