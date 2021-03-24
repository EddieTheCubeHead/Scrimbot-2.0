__version__ = "0.1"
__author__ = "Eetu Asikainen"

from enum import Enum

class ScrimState(Enum):
    INACTIVE = 1
    LFP = 2
    CAPS = 3
    LOCKED = 4
    STARTED = 5