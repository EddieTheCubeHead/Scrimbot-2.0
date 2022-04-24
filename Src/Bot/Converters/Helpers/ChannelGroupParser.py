__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
import re

from discord import CategoryChannel, VoiceChannel

from Bot.Core.BotDependencyInjector import BotDependencyInjector


@BotDependencyInjector.singleton
class ChannelGroupParser:

    def parse(self, channel_group: CategoryChannel) -> list[tuple[VoiceChannel, int]]:
        if len(channel_group.voice_channels) < 3:
            return self._parse_small_group(channel_group.voice_channels)
        names = [channel.name for channel in channel_group.voice_channels]
        names.sort(key=lambda name: (len(name), name))
        team_prefix, team_suffix = self._get_prefix_and_suffix(names[:3])
        voice_channels = self._parse_channels(channel_group.voice_channels, team_prefix, team_suffix)
        voice_channels.sort(key=lambda channel: channel[1])
        return voice_channels

    # This is all kinds of wonky so I'll include some explaining comments
    def _get_prefix_and_suffix(self, names: list[str]) -> tuple[str, str]:
        # Take three shortest channel names (sort equal lengths alphabetically) as they will always contain channels
        # for teams 1 and 2, if present and either channel for team 3, or lobby channel and get common prefixes and
        # suffixes for all combinations of the three.
        prefix_suffix_pairs = self._get_prefix_suffix_pairs(names)

        # Lobby can only be the first or last item of the sorted channel name list as team 1 and 2 have no room
        # between them alphabetically, save for a longer name that is prefixed by team 1 channel name. This is not
        # possible here, as the primary sorting condition for channels is length. Assuming only valid input data, if
        # lobby is first, team 1 and 2 channel shared prefix is always last in the prefix suffix pair list. Otherwise
        # either all three channels are team voice channels, in which case all prefix suffix pairs are valid, or the
        # first two are team voice channels, in which case the first pair is valid so the first case is always valid.
        if self._first_is_lobby(names, prefix_suffix_pairs):
            return prefix_suffix_pairs[2]
        return prefix_suffix_pairs[0]

    def _get_prefix_suffix_pairs(self, names) -> list[tuple[str, str]]:
        prefix_suffix_pairs = []
        for index, name in enumerate(names, 1):
            for compared in names[index:]:
                prefix_suffix_pairs.append(self._get_common_prefix_and_suffix(name, compared))
        return prefix_suffix_pairs

    @staticmethod
    def _get_common_prefix_and_suffix(name, compared):
        return str(os.path.commonprefix((name, compared))),\
               str(os.path.commonprefix((name[::-1], compared[::-1])))[::-1]

    def _first_is_lobby(self, names, prefix_suffix_pairs):
        return self._first_name_is_shortest(names) or (self._all_names_are_equal_length(names)
                                                       and not self._all_pairs_are_equal(prefix_suffix_pairs))

    @staticmethod
    def _first_name_is_shortest(names):
        return len(names[0]) < len(names[1]) == len(names[2])

    @staticmethod
    def _all_names_are_equal_length(names):
        return len(names[0]) == len(names[1]) == len(names[2])

    @staticmethod
    def _all_pairs_are_equal(prefix_suffix_pairs):
        return not prefix_suffix_pairs[0] == prefix_suffix_pairs[1] == prefix_suffix_pairs[2]

    def _parse_channels(self, voice_channels, team_prefix, team_suffix) -> list[tuple[VoiceChannel, int]]:
        channels, teams = [], []
        for channel in voice_channels:
            channel_team = self._parse_channel(channel, team_prefix, team_suffix)
            channels.append(channel)
            teams.append(channel_team)
        return list(zip(channels, teams))

    @staticmethod
    def _parse_channel(channel, team_prefix, team_suffix) -> int:
        expected_team_literal = re.search(r"(^\d*)", channel.name[len(team_prefix):]).group(0)
        if not channel.name == team_prefix + expected_team_literal + team_suffix:
            return 0
        return int(expected_team_literal)

    @staticmethod
    def _parse_small_group(voice_channels) -> list[tuple[VoiceChannel, int]]:
        if len(voice_channels) == 1:
            return [(voice_channels[0], 0)]
        return [(voice_channels[0], 1), (voice_channels[1], 2)]
