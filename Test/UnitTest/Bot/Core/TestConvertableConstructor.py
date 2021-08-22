__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.Convertable import Convertable
from Bot.Converters.ConverterBase import ConverterBase
from Bot.Exceptions.BuildException import BuildException
from Database.DatabaseConnections.ConnectionBase import ConnectionBase
from Utils.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestIdGenerator import TestIdGenerator
from Bot.Core.ConvertableConstructor import ConvertableConstructor, strip_name


class TestConvertableConstructor(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        ConvertableConstructor.convertables = {}
        ConvertableConstructor.converters = {}
        ConvertableConstructor.connections = {}

    async def test_build_given_convertable_converter_and_connection_present_then_injected_and_constructed(self):

        @ConvertableConstructor.convertable
        class MockConvertable(Convertable):
            pass

        @ConvertableConstructor.converter
        class MockConvertableConverter(ConverterBase):
            async def convert(self, argument: str):
                return f"Converted {self.connection.get_from_id(int(argument))}"

        @ConvertableConstructor.connection
        class MockConvertableConnection(ConnectionBase):
            def get_from_id(self, object_id: int):
                return f"Entry {object_id}"

        constructor = ConvertableConstructor("Database.Path")
        constructor.build()
        mock_entry = str(self.id_generator.generate_viable_id())
        self.assertEqual(f"Converted Entry {mock_entry}", await MockConvertable.convert(mock_entry))

    def test_build_given_convertable_with_no_converter_but_connection_then_error_raised_with_missing_converter(self):
        @ConvertableConstructor.convertable
        class MockConvertable(Convertable):
            pass

        @ConvertableConstructor.converter
        class InvalidConverter(ConverterBase):
            pass

        @ConvertableConstructor.connection
        class MockConvertableConnection(ConnectionBase):
            pass

        expected_exception = BuildException("Could not find associated converter for convertable"
                                            " 'MockConvertable' during bot initialization.")
        constructor = ConvertableConstructor("Database.Path")
        self._assert_raises_correct_exception(expected_exception, constructor.build)

    def test_build_given_convertable_with_no_converter_and_connection_then_error_raised_with_missing_converter(self):
        @ConvertableConstructor.convertable
        class MockConvertable(Convertable):
            pass

        @ConvertableConstructor.converter
        class InvalidConverter(ConverterBase):
            pass

        @ConvertableConstructor.connection
        class InvalidConnection(ConnectionBase):
            pass

        expected_exception = BuildException("Could not find associated converter for convertable"
                                            " 'MockConvertable' during bot initialization.")
        constructor = ConvertableConstructor("Database.Path")
        self._assert_raises_correct_exception(expected_exception, constructor.build)

    def test_build_given_convertable_with_converter_but_no_connection_then_error_raised_with_missing_connection(self):
        @ConvertableConstructor.convertable
        class MockConvertable(Convertable):
            pass

        @ConvertableConstructor.converter
        class MockConvertableConverter(ConverterBase):
            pass

        @ConvertableConstructor.connection
        class InvalidConnection(ConnectionBase):
            pass

        expected_exception = BuildException("Could not find associated connection for convertable"
                                            " 'MockConvertable' during bot initialization.")
        constructor = ConvertableConstructor("Database.Path")
        self._assert_raises_correct_exception(expected_exception, constructor.build)

    def test_strip_name_given_postfix_and_conforming_name_then_postfix_stripped_correctly(self):
        postfix = "Converter"

        class MockConvertableConverter:
            pass

        self.assertEqual("MockConvertable", strip_name(MockConvertableConverter, postfix))

    def test_strip_name_given_postfix_and_non_conforming_name_then_error_raised_with_information(self):
        postfix = "Converter"

        class MockConvertableCovfefe:
            pass

        expected_exception = BuildException("Dependency injection failed. Possible spelling error in the name of class "
                                            f"'{MockConvertableCovfefe.__name__}'.")
        self._assert_raises_correct_exception(expected_exception, strip_name, MockConvertableCovfefe, postfix)
