__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Any, Union

from Src.Bot.Core.ScrimContext import ScrimContext


class MockedCall:

    def __init__(self, args: Union[str, list[str]], return_value: Any, *ctx_matches: tuple[list[str], Any]):
        self.args: list[str] = args if type(args) == list else [args]
        self.return_value: Any = return_value
        self.ctx_matches: tuple[tuple[list[str], Any]] = ctx_matches

    def matches(self, ctx: ScrimContext, arg: str) -> bool:
        return arg in self.args and self._ctx_matches(ctx)

    def _ctx_matches(self, ctx: ScrimContext) -> bool:
        for ctx_match_path, ctx_match_value in self.ctx_matches:
            matched = ctx
            for attribute in ctx_match_path:
                try:
                    matched = matched.__getattribute__(attribute)
                except AttributeError:
                    return False
            if not matched == ctx_match_value:
                break
        else:
            return True
        return False


class MockDiscordConverter:

    def __init__(self):
        self.mock_values: list[MockedCall] = []

    def __call__(self, *args, **kwargs):
        return self

    def add_mock_call(self, args: Union[str, list[str]], return_value, *ctx_matches: tuple[list[str], Any]):
        self.mock_values.append(MockedCall(args, return_value, *ctx_matches))

    async def convert(self, ctx: ScrimContext, arg: str):
        for mock_value in self.mock_values:
            if mock_value.matches(ctx, arg):
                return mock_value.return_value

