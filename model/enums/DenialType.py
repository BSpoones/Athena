from enum import Enum

class DenialType(Enum):
    NONE = 0
    ABSOLUTE = 1
    CONSENT_BASED = 2
    HARM = 3
    IGNORANCE = 4
    INVERSION = 5
    JUSTIFIED = 6
    REDEFINITION = 7
    SELECTIVE = 8
