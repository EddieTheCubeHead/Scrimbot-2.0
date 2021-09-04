__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Dict, Tuple, List
import re

from discord.ext import commands


class BotHelpCommand(commands.DefaultHelpCommand):
    """A custom help command implementation for the bot.

    methods
    -------

    add_command_formatting(command)
        An overridden method from DefaultHelpCommand responsible for adding helps string into the paginator
    """

    # A dict for converting actual python type hint strings into more user friendly explanations. Note that optionals
    # are ignored as they are explained in another part of the help command
    _user_type_hints: Dict[str, str] = {
        "str": "a string",
        "Optional[discord.VoiceChannel]": "a string representing a voice channel",
        "Game": "a string representing a game known by the bot, or an alias of one (see command 'listgames')",
        "Optional[int]": "a whole number",
        "bool": "a string representing a truth value (true/false)"
    }

    def __init__(self, dm_help=True):
        """A custom constructor for BotHelpCommand

        args
        ----

        :param dm_help: Whether the bot should sent help messages as dms instead of to the invokation context
        :type dm_help: Optional[bool]
        """

        super().__init__(dm_help=dm_help)

    def add_command_formatting(self, command: commands.Command):
        """An override from DefaultHelpCommand. Responsible for adding the custom help string into the paginator.

        args
        ----

        :param command: The command for which a help message should be constructed
        :type command: commands.Command
        """

        desc, param_data = self._command_doc_parser(command.help)
        self._help_command_builder(command, desc, param_data)

    def _command_doc_parser(self, docstring: str) -> Tuple[str, List[Tuple[str, str, str]]]:
        """A private helper method for parsing a command's docstring.

        args
        ----

        :param docstring: The docstring that should be parsed:
        :type docstring: str
        :return: A tuple containing the command description and a list of str, str, str tuples with readable param data
        :rtype: tuple[str, list[tuple[str, str, str]]]
        """

        lines: List[str] = docstring.split("\n")
        desc = lines[0]
        current_name = []
        current_param = []
        current_types = []
        for line in lines[1:]:
            if line.lstrip().startswith(":param") and not line.lstrip().startswith(":param ctx:"):
                current_name.append(line.split(":")[1].split(" ")[1].strip())
                current_param.append(":".join(line.split(":")[2:]).strip())
            elif line.strip().startswith(":type") and not line.strip().startswith(":type ctx:"):
                current_types.append(":".join(line.split(":")[2:]).strip())

        param_types = list(zip(current_name, current_param, current_types))

        return desc, param_types

    def _matches_optional(self, param: str):
        """A private helper method returning whether a param type string matches typing.Optional[type]"""
        return re.fullmatch(r"Optional[.*]", param)

    def _help_command_builder(self, command: commands.Command, description: str,
                              param_data: List[Tuple[str, str, str]]):
        """A private helper method for building a help command's text out of data given

        args
        ----

        :param command: The command object that a help message should be constructed for
        :type command: commands.Command
        :param description: The description of the command, first line of the command's docstring
        :type description: str
        :param param_data: A list of each parameter's data for the command, gotten from _command_doc_parser
        :type param_data: list[tuple[str, str, str]]
        """

        self.paginator.add_line(description, empty=True)

        self.paginator.add_line(f"Usage: {self.context.prefix}{command.name} {command.signature}", empty=True)

        if param_data:
            self.paginator.add_line("Parameters:", empty=True)

        for param in param_data:
            self.paginator.add_line(f"{param[0]}{' (optional)' if self._matches_optional(param[2]) else ''}:"
                                    f" {param[1]}, should be given as {self._user_type_hints[param[2]]}", empty=True)

        if command.aliases:
            self.paginator.add_line(f"Aliases: {command.aliases}")
