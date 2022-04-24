__version__ = "0.1"
__author__ = "Eetu Asikainen"

import datetime

from behave import *

from Test.Utils.TestHelpers.DatetimePatcher import DatetimePatcher


@when("{amount} minutes elapses")
def step_impl(context, amount):
    mock_datetime = DatetimePatcher(datetime.datetime.now, minutes=int(amount))
    context.patcher.add_patch("datetime.datetime", mock_datetime)
