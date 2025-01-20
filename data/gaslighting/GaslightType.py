from enum import Enum


class GaslightType(Enum):
    DENIAL = 1 # "This never happened, you're imagining it"
    CONTRADICTION = 2 # "I never said X, you're making things up"
    FALSE_REASSURANCE = 3 # "You've overthinking X, you always do this"
    BLAME_SHIFTING = 4 # "If you didn't do X, this wouldn't be a problem"
    DIVERTING = 5 # "Why are you bring up things that don't matter?"
    
    def get(ordinal: int):
        return 0
    
    def min(): int = 0
    def max(): int = 0