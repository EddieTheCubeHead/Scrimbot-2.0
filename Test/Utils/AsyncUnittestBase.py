__version__ = "0.1"
__author__ = "Eetu Asikainen"


from unittest import IsolatedAsyncioTestCase

from Utils.UnittestBase import UnittestBase


class AsyncUnittestBase(UnittestBase, IsolatedAsyncioTestCase):
    pass
