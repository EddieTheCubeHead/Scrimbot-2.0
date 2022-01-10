__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Exceptions.BuildException import BuildException
from Test.Utils.TestBases.UnittestBase import UnittestBase


class TestBuildException(UnittestBase):

    def test_msg_given_failure_string_then_description_includes_build_data_and_contact_information(self):

        exception_string = "Test failure"
        exception = BuildException(exception_string)
        expected_message = f"An error occurred during build: {exception_string}\n" \
                           f"If you have not modified the source code, please file a bug report in the bot " \
                           f"repository in GitHub according to the guidelines of a good bug report."
        self.assertEqual(expected_message, exception.__str__())
