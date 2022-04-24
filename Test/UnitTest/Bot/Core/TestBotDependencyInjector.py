from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from discord.ext.commands import Context
from sqlalchemy import Column, Integer

from Bot.Converters.Convertable import Convertable
from Bot.DataClasses.DataClass import DataClass
from Bot.Converters.ConverterBase import ConverterBase
from Bot.Exceptions.BotLoggedNoContextException import BotLoggedNoContextException
from Bot.Exceptions.BuildException import BuildException
from Database.DatabaseConnections.ConnectionBase import ConnectionBase
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Bot.Core.BotDependencyInjector import BotDependencyInjector


class TestInjector(BotDependencyInjector):  # isolate test cases here to allow resetting constructor
    pass


class TestBotDependencyConstructor(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        TestInjector.singletons = {}

    async def test_singleton_given_dataclass_converter_and_connection_singletons_then_dependencies_injected(self):

        class MockSingletonDataClass(DataClass, Convertable):
            id = Column(Integer, primary_key=True)

            def __init__(self, message: str):
                self.message = message

            @classmethod
            @TestInjector.inject
            def set_converter(cls, converter: MockSingletonConverter):
                super().set_converter(converter)

        @TestInjector.singleton
        class MockSingletonConverter(ConverterBase[MockSingletonDataClass]):

            @TestInjector.inject
            def __init__(self, connection: MockSingletonConnection):
                super().__init__(connection)

            async def convert(self, ctx: Context, argument: str):
                return MockSingletonDataClass(f"Converted {self.connection.get_from_id(int(argument))}")

        @TestInjector.singleton
        class MockSingletonConnection(ConnectionBase[MockSingletonDataClass]):

            @staticmethod
            def get_from_id(object_id: int):
                return f"Entry {object_id}"

        mock_entry = str(self.id_generator.generate_viable_id())
        self.assertEqual(f"Converted Entry {mock_entry}",
                         (await MockSingletonDataClass.convert(MagicMock(), mock_entry)).message)

    async def test_instance_given_dataclass_converter_and_connection_singletons_then_dependencies_injected(self):

        class MockInstanceDataClass(DataClass, Convertable):
            id = Column(Integer, primary_key=True)

            def __init__(self, message: str):
                self.message = message

            @classmethod
            @TestInjector.inject
            def set_converter(cls, converter: MockInstanceConverter):
                super().set_converter(converter)

        @TestInjector.instance
        class MockInstanceConverter(ConverterBase[MockInstanceDataClass]):

            @TestInjector.inject
            def __init__(self, connection: MockInstanceConnection):
                super().__init__(connection)

            async def convert(self, ctx: Context, argument: str):
                return MockInstanceDataClass(f"Converted {self.connection.get_from_id(int(argument))}")

        @TestInjector.instance
        class MockInstanceConnection(ConnectionBase[MockInstanceDataClass]):

            @staticmethod
            def get_from_id(object_id: int):
                return f"Entry {object_id}"

        mock_entry = str(self.id_generator.generate_viable_id())
        self.assertEqual(f"Converted Entry {mock_entry}",
                         (await MockInstanceDataClass.convert(MagicMock(), mock_entry)).message)

    def test_inject_given_function_with_default_arguments_then_default_arguments_not_injected(self):

        @BotDependencyInjector.instance
        class Injectable:

            def __init__(self, value: int = 1):
                self.value = value

        @BotDependencyInjector.inject
        def default_test(argument: Injectable, another: Injectable = Injectable(2)):
            return another.value > argument.value

        self.assertTrue(default_test())

    def test_inject_given_method_then_self_argument_not_injected(self):

        @BotDependencyInjector.singleton
        class Injectable:

            def __init__(self, value: int = 1):
                self.value = value

        class Dependent:

            @BotDependencyInjector.inject
            def __init__(self, injectable: Injectable):
                self.injectable = injectable

        self.assertEqual(Injectable().value, Dependent().injectable.value)

    def test_inject_given_args_list_then_args_not_injected(self):

        @BotDependencyInjector.singleton
        class Injectable:

            def __init__(self, value: bool = True):
                self.value = value

        @BotDependencyInjector.inject
        def args_test(argument: Injectable, *args):
            return argument.value and not args

        self.assertTrue(args_test)

    def test_inject_given_kwargs_then_kwargs_not_injected(self):

        @BotDependencyInjector.singleton
        class Injectable:

            def __init__(self, value: bool = True):
                self.value = value

        @BotDependencyInjector.inject
        def kwargs_test(argument: Injectable, **kwargs):
            return argument.value and not kwargs

        self.assertTrue(kwargs_test)

    def test_inject_given_class_method_with_default_args_and_kwargs_then_only_dependencies_injected(self):

        @BotDependencyInjector.singleton
        class Injectable:

            def __init__(self, value: bool = True):
                self.value = value

        class Dependent:

            @BotDependencyInjector.inject
            def __init__(self, injectable: Injectable, default: bool = True, *args, **kwargs):
                self.injectable = injectable
                self.default = default
                self.args = args
                self.kwargs = kwargs

            def __bool__(self):
                return self.injectable and self.default and not self.args and not self.kwargs

        self.assertTrue(Dependent())

    def test_inject_given_dependency_with_no_resolution_then_error_raised_with_missing_dependency(self):

        class DependentClass:
            @TestInjector.inject
            def __init__(self, dependency: Dependency):
                self.dependency = dependency

        class Dependency:
            pass

        expected_exception = BuildException(f"Could not inject argument dependency because type '{Dependency.__name__}'"
                                            f" is not registered as a dependency.")
        self._assert_raises_correct_exception(expected_exception, DependentClass)

    def test_inject_given_dependency_with_no_annotation_then_error_raised_with_missing_annotation(self):

        class DependentClass:
            @TestInjector.inject
            def __init__(self, dependency):
                self.dependency = dependency

        expected_exception = BuildException(f"Could not inject argument dependency because it doesn't have a type"
                                            f" annotation.")
        self._assert_raises_correct_exception(expected_exception, DependentClass)

    def test_singleton_given_instance_dependency_of_same_type_then_error_raised_with_duplicate_annotation(self):

        @BotDependencyInjector.instance
        class DuplicatedDependency:
            pass

        expected_exception = BuildException(f"Could not register dependency {DuplicatedDependency.__name__} as a "
                                            f"dependency with identical name already exists.")
        self._assert_raises_correct_exception(expected_exception, BotDependencyInjector.singleton, DuplicatedDependency)

    def test_singleton_given_singleton_dependency_of_same_type_then_error_raised_with_duplicate_annotation(self):

        @BotDependencyInjector.singleton
        class DuplicatedDependency:
            pass

        expected_exception = BuildException(f"Could not register dependency {DuplicatedDependency.__name__} as a "
                                            f"dependency with identical name already exists.")
        self._assert_raises_correct_exception(expected_exception, BotDependencyInjector.singleton, DuplicatedDependency)

    def test_instance_given_instance_dependency_of_same_type_then_error_raised_with_duplicate_annotation(self):

        @BotDependencyInjector.instance
        class DuplicatedDependency:
            pass

        expected_exception = BuildException(f"Could not register dependency {DuplicatedDependency.__name__} as a "
                                            f"dependency with identical name already exists.")
        self._assert_raises_correct_exception(expected_exception, BotDependencyInjector.instance, DuplicatedDependency)

    def test_instance_given_singleton_dependency_of_same_type_then_error_raised_with_duplicate_annotation(self):

        @BotDependencyInjector.singleton
        class DuplicatedDependency:
            pass

        expected_exception = BuildException(f"Could not register dependency {DuplicatedDependency.__name__} as a "
                                            f"dependency with identical name already exists.")
        self._assert_raises_correct_exception(expected_exception, BotDependencyInjector.instance, DuplicatedDependency)
