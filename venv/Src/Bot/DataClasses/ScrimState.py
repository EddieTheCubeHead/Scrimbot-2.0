__version__ = "0.1"
__author__ = "Eetu Asikainen"

from enum import Enum

class ScrimState(Enum):
    """A simple enum class to ease the state management of scrims"""

    INACTIVE = 1
    LFP = 2
    CAPS_PREP = 3
    CAPS = 4
    LOCKED = 5
    STARTED = 6
