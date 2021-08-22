__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Type, Any

from Bot.Converters.Convertable import Convertable
from Bot.Converters.ConverterBase import ConverterBase
from Database.DatabaseConnections.ConnectionBase import ConnectionBase
from Bot.Exceptions.BuildException import BuildException


def strip_name(base_class: Any, trailing_string: str):
    if not base_class.__name__[-len(trailing_string):] == trailing_string:
        raise BuildException(f"Dependency injection failed. Possible spelling error in the name of class "
                             f"'{base_class.__name__}'.")
    return base_class.__name__[:-len(trailing_string)]


class ConvertableConstructor:

    convertables: dict[str, Type[Convertable]] = {}
    converters = {}
    connections = {}

    def __init__(self, db_path: str):
        self._db_path = db_path

    @classmethod
    def convertable(cls, convertable: Type[Convertable]):
        cls.convertables[convertable.__name__] = convertable
        return convertable

    @classmethod
    def converter(cls, converter: ConverterBase):
        cls.converters[strip_name(converter, "Converter")] = converter
        return converter

    @classmethod
    def connection(cls, connection: ConnectionBase):
        cls.connections[strip_name(connection, "Connection")] = connection
        return connection

    def build(self):
        for convertable in self.convertables:
            self._build_convertable(convertable)

    def _build_convertable(self, convertable: str):
        self._assert_dependencies_fulfilled(convertable)
        connection = self.connections[convertable](self._db_path)
        converter = self.converters[convertable](connection)
        self.convertables[convertable].set_converter(converter)

    def _assert_dependencies_fulfilled(self, convertable):
        if convertable not in self.converters:
            raise BuildException(f"Could not find associated converter for convertable '{convertable}' during bot "
                                 f"initialization.")
        if convertable not in self.connections:
            raise BuildException(f"Could not find associated connection for convertable '{convertable}' during bot "
                                 f"initialization.")
