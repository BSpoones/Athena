from model.lib.util.enums.ElementTypeEnum import ElementType

class ThreatType(ElementType):
    EXPLICIT = 1
    IMPLICIT = 2
    REPUTATION = 3
    SELF_HARM = 4

    @property
    def raw_file(self) -> str:
        return ""

    @property
    def paraphrased_file(self) -> str:
        return ""

    @property
    def normalised_file(self) -> str:
        return ""

    @property
    def classified_file(self) -> str:
        return ""