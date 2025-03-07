from model.lib.util.enums.ElementTypeEnum import ElementType

class DenialType(ElementType):
    ABSOLUTE = 1
    CONSENT_BASED = 2
    HARM = 3
    IGNORANCE = 4
    INVERSION = 5
    JUSTIFIED = 6
    REDEFINITION = 7
    SELECTIVE = 8

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