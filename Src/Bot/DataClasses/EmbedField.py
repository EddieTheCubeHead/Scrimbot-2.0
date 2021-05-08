__version__ = "0.1"
__author__ = "Eetu Asikainen"


class EmbedField:
    """A class that houses all data required to construct a field in the embed.

    Currently used as is for the divider field and inherited for the ScrimTeam class so teams can be easily displayed as
    embed fields.

    ----------
    attributes

    inline: bool
        Whether the field should be attempted to display inline with other inline=True fields

    -------
    methods

    get_name() -> str
        Get the name field value of the embed field

    get_value() -> str
        Get the value field value of the embed field
    """

    def __init__(self, name, value, inline):
        self._name: str = name
        self._value: str = value
        self.inline: bool = inline

    def get_name(self) -> str:
        return self._name

    def get_value(self) -> str:
        return self._value
