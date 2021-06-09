__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest

from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class TestScrimTeamsManager(unittest.TestCase):

    def setUp(self) -> None:
        self.manager = ScrimTeamsManager(5, 2, True)

    def test_test(self):
        pass
