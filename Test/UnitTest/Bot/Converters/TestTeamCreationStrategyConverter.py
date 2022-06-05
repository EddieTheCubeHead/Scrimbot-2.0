__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.TeamCreationStrategyConverter import TeamCreationStrategyConverter
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestTeamCreationStrategyConverter(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.converter = TeamCreationStrategyConverter()
        self.mock_context = MagicMock()

    async def test_convert_given_strategy_in_dict_then_strategy_returned(self):
        mock_strategies = {
            "1": MagicMock(),
            "2": MagicMock(),
            "3": MagicMock()
        }
        TeamCreationStrategyConverter._strategies = mock_strategies
        for strategy in mock_strategies:
            with self.subTest(f"Converting TeamCreationStrategy with string argument '{strategy}'"):
                strategy_impl = await self.converter.convert(self.mock_context, strategy)
                self.assertEqual(mock_strategies[strategy], strategy_impl)

    def test_register_given_class_decorated_with_arg_then_class_added_to_dict_with_arg_as_key(self):
        @TeamCreationStrategyConverter.register("test")
        class MockConverter:
            pass

        self.assertIn("test", TeamCreationStrategyConverter._strategies)
        self.assertEqual(type(MockConverter()), type(TeamCreationStrategyConverter._strategies["test"]))
