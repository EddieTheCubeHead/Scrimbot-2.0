__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy import Column, Integer

from Bot.DataClasses.Convertable import Convertable
from Bot.Converters.ConverterBase import ConverterBase
from Bot.Exceptions.BuildException import BuildException
from Database.DatabaseConnections.ConnectionBase import ConnectionBase
from Utils.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestIdGenerator import TestIdGenerator
from Bot.Core.BotDependencyConstructor import BotDependencyConstructor, get_convertable_type


class TestBotDependencyConstructor(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        BotDependencyConstructor.convertables = {}
        BotDependencyConstructor.converters = {}
        BotDependencyConstructor.connections = {}

    async def test_build_given_convertable_converter_and_connection_present_then_injected_and_constructed(self):

        @BotDependencyConstructor.convertable
        class MockConvertable(Convertable):
            id = Column(Integer, primary_key=True)

            def __init__(self, message: str):
                self.message = message

        @BotDependencyConstructor.converter
        class MockConvertableConverter(ConverterBase[MockConvertable]):
            async def convert(self, argument: str):
                return MockConvertable(f"Converted {self.connection.get_from_id(int(argument))}")

        @BotDependencyConstructor.connection
        class MockConvertableConnection(ConnectionBase[MockConvertable]):
            def get_from_id(self, object_id: int):
                return f"Entry {object_id}"

            def get_multiple(self, *object_ids: int) -> list[MockConvertable]:
                pass

            def get_all(self) -> list[MockConvertable]:
                pass

            def update(self, updated_object: MockConvertable):
                pass

            def insert(self, new_object: MockConvertable):
                pass

        constructor = BotDependencyConstructor("Database.Path")
        constructor.build()
        mock_entry = str(self.id_generator.generate_viable_id())
        self.assertEqual(f"Converted Entry {mock_entry}", (await MockConvertable.convert(mock_entry)).message)

    def test_build_given_convertable_with_no_converter_but_connection_then_error_raised_with_missing_converter(self):
        @BotDependencyConstructor.convertable
        class MockConvertable2(Convertable):
            id = Column(Integer, primary_key=True)

        @BotDependencyConstructor.converter
        class MockConvertableConverter(ConverterBase[Convertable]):
            pass

        @BotDependencyConstructor.connection
        class MockConvertableConnection(ConnectionBase[MockConvertable2]):
            def get_from_id(self, object_id: int):
                return f"Entry {object_id}"

            def get_multiple(self, *object_ids: int) -> list[MockConvertable2]:
                pass

            def get_all(self) -> list[MockConvertable2]:
                pass

            def update(self, updated_object: MockConvertable2):
                pass

            def insert(self, new_object: MockConvertable2):
                pass

        expected_exception = BuildException("Could not find associated converter for convertable"
                                            " 'MockConvertable2' during bot initialization.")
        constructor = BotDependencyConstructor("Database.Path")
        self._assert_raises_correct_exception(expected_exception, constructor.build)

    def test_build_given_convertable_with_no_converter_and_connection_then_error_raised_with_missing_converter(self):
        @BotDependencyConstructor.convertable
        class MockConvertable3(Convertable):
            id = Column(Integer, primary_key=True)

        @BotDependencyConstructor.converter
        class InvalidConverter(ConverterBase[Convertable]):
            pass

        @BotDependencyConstructor.connection
        class InvalidConnection(ConnectionBase[Convertable]):
            pass

        expected_exception = BuildException("Could not find associated converter for convertable"
                                            " 'MockConvertable3' during bot initialization.")
        constructor = BotDependencyConstructor("Database.Path")
        self._assert_raises_correct_exception(expected_exception, constructor.build)

    def test_build_given_convertable_with_converter_but_no_connection_then_error_raised_with_missing_connection(self):
        @BotDependencyConstructor.convertable
        class MockConvertable4(Convertable):
            id = Column(Integer, primary_key=True)

        @BotDependencyConstructor.converter
        class MockConvertableConverter(ConverterBase[MockConvertable4]):
            pass

        @BotDependencyConstructor.connection
        class InvalidConnection(ConnectionBase[Convertable]):
            pass

        expected_exception = BuildException("Could not find associated connection for convertable"
                                            " 'MockConvertable4' during bot initialization.")
        constructor = BotDependencyConstructor("Database.Path")
        self._assert_raises_correct_exception(expected_exception, constructor.build)

    def test_build_given_duplicate_converters_then_error_raised_with_duplicate_info(self):
        @BotDependencyConstructor.convertable
        class MockConvertable5(Convertable):
            id = Column(Integer, primary_key=True)

        @BotDependencyConstructor.converter
        class MockConvertableConverter(ConverterBase[MockConvertable5]):
            pass

        class InvalidConverter(ConverterBase[MockConvertable5]):
            pass

        expected_exception = BuildException(f"Received duplicate converters for convertable "
                                            f"'{MockConvertable5.__name__}' ({MockConvertableConverter.__name__} and "
                                            f"{InvalidConverter.__name__}).")
        self._assert_raises_correct_exception(expected_exception, BotDependencyConstructor.converter, InvalidConverter)

    def test_build_given_duplicate_connections_then_error_raised_with_duplicate_info(self):
        @BotDependencyConstructor.convertable
        class MockConvertable6(Convertable):
            id = Column(Integer, primary_key=True)

        @BotDependencyConstructor.connection
        class MockConvertableConnection(ConnectionBase[MockConvertable6]):
            pass

        class InvalidConnection(ConnectionBase[MockConvertable6]):
            pass

        expected_exception = BuildException(f"Received duplicate connections for convertable "
                                            f"'{MockConvertable6.__name__}' ({MockConvertableConnection.__name__} and "
                                            f"{InvalidConnection.__name__}).")
        self._assert_raises_correct_exception(expected_exception, BotDependencyConstructor.connection, InvalidConnection)

    def test_get_convertable_name_given_no_generic_type_then_error_raised_with_disclaimer(self):
        class InvalidClass:
            pass
        expected_exception = BuildException(f"Class '{InvalidClass.__name__}' lacks generic convertable info "
                                            f"or does not inherit neither of ConverterBase or ConnectionBase.")
        self._assert_raises_correct_exception(expected_exception, get_convertable_type, InvalidClass)

    def test_get_convertable_name_given_wrong_generic_type_then_error_raised_with_disclaimer(self):
        invalid_type = int
        class InvalidClass(ConverterBase[invalid_type]):
            pass
        expected_exception = BuildException(f"Class '{InvalidClass.__name__}' has generic type "
                                            f"'{invalid_type.__name__}' which is not a subtype of Convertable")
        self._assert_raises_correct_exception(expected_exception, get_convertable_type, InvalidClass)
