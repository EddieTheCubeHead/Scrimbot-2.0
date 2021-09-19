__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Callable
from unittest import IsolatedAsyncioTestCase

from Utils.TestBases.UnittestBase import UnittestBase


class AsyncUnittestBase(UnittestBase, IsolatedAsyncioTestCase):

    async def _async_assert_raises_correct_exception(self, excepted_exception: Exception, call: Callable, *args, **kwargs):
        with self.assertRaises(type(excepted_exception)) as context:
            await call(*args, **kwargs)

        self.assertEqual(str(excepted_exception), str(context.exception))
        return context.exception
