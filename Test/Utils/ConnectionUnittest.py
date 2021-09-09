__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Generic, TypeVar, Any, get_args

from Utils.UnittestBase import UnittestBase
from Bot.DataClasses.DataClass import DataClass

T = TypeVar('T', bound=DataClass)


class ConnectionUnittest(UnittestBase, Generic[T]):

    def _assert_successful_fetch(self, fetched: Any):
        self.assertIsNotNone(fetched)
        # noinspection PyUnresolvedReferences
        base_class = self.__orig_bases__[0]
        generic = get_args(base_class)[0]
        self.assertEqual(generic, type(fetched))
