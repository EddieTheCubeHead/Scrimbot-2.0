__version__ = "0.1"
__author__ = "Eetu Asikainen"

from enum import Enum


class ScrimState(Enum):
    """A simple enum class to ease the state management of scrims"""

    INACTIVE = "inactive"
    LFP = "looking for players"
    CAPS_PREP = "waiting to choose captains"
    CAPS = "letting captains pick players"
    LOCKED = "waiting for team selection"
    VOICE_WAIT = "waiting for players to join voice channel"
    STARTED = "underway"
