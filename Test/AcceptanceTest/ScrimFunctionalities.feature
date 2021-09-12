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