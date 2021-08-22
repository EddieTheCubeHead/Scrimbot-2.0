__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Type, Any, get_args

from Bot.Converters.Convertable import Convertable
from Bot.Converters.ConverterBase import ConverterBase
from Database.DatabaseConnections.ConnectionBase import ConnectionBase
from Bot.Exceptions.BuildException import BuildException


def get_convertable_type(derived_class) -> str:
    generic = _get_generic_from_base(derived_class)
    if not issubclass(generic, Convertable):
        raise BuildException(f"Class '{derived_class.__name__}' has generic type '{generic.__name__}' which is not a "
                             f"subtype of Convertable")
    return generic.__name__


def _get_generic_from_base(derived_class):
    try:
        base_class = derived_class.__orig_bases__[0]
        generic = get_args(base_class)[0]
    except Exception:
        raise BuildException(f"Class '{derived_class.__name__}' lacks generic convertable info or does not inherit "
                             f"neither of ConverterBase or ConnectionBase.")
    return generic


class ConvertableConstructor:

    convertables: dict[str, Type[Convertable]] = {}
    converters: dict[str, ConverterBase] = {}
    connections: dict[str, ConnectionBase] = {}

    def __init__(self, db_path: str):
        self._db_path = db_path

    @classmethod
    def convertable(cls, convertable: Type[Convertable]):
        cls.convertables[convertable.__name__] = convertable
        return convertable

    @classmethod
    def converter(cls, converter: ConverterBase):
        # noinspection PyTypeChecker
        convertable_name = get_convertable_type(converter)
        if convertable_name in cls.converters:
            raise BuildException(f"Received duplicate converters for convertable '{convertable_name}' "
                                 f"({cls.converters[convertable_name].__name__} and {converter.__name__}).")
        cls.converters[convertable_name] = converter
        return converter

    @classmethod
    def connection(cls, connection: ConnectionBase):
        # noinspection PyTypeChecker
        connection_name = get_convertable_type(connection)
        if connection_name in cls.connections:
            raise BuildException(f"Received duplicate connections for convertable '{connection_name}' "
                                 f"({cls.connections[connection_name].__name__} and {connection.__name__}).")
        cls.connections[connection_name] = connection
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
