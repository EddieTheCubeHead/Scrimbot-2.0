__version__ = "0.1"
__author__ = "Eetu Asikainen"


import unittest
from typing import Callable


class UnittestBase(unittest.TestCase):

    def _assert_raises_correct_exception(self, excepted_exception: Exception, call: Callable, *args, **kwargs):
        with self.assertRaises(type(excepted_exception)) as context:
            call(*args, **kwargs)

        self.assertEqual(str(excepted_exception), str(context.exception))
        return context.exception
