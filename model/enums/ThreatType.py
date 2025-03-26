from enum import Enum

class ThreatType(Enum):
    NONE = 0
    EXPLICIT = 1
    IMPLICIT = 2
    REPUTATION = 3
    SELF_HARM = 4