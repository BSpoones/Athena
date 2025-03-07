from model.lib.util.enums.ElementTypeEnum import ElementType

class PowerImbalanceType(ElementType):
    AUTHORITY = 1
    KNOWLEDGE = 2
    RESOURCE = 3

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