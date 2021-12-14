__version__ = "0.1"
__author__ = "Eetu Asikainen"


class BuildException(Exception):

    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"An error occurred during build: {self.message}\n" \
               f"If you have not modified the source code, please file a bug report in the bot repository in GitHub " \
               f"according to the guidelines of a good bug report."