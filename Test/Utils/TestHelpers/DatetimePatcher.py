__version__ = "0.1"
__author__ = "Eetu Asikainen"

import datetime


class DatetimePatcher:

    def __init__(self, func, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0):
        self._original_function = func
        self._timedelta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

    def now(self):
        return self._original_function() + self._timedelta
