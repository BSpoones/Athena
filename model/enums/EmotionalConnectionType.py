from model.lib.util.enums.ElementTypeEnum import ElementType

class EmotionalConnectionType(ElementType):
    AFFECTION = 1
    GUILT = 2
    POSSESSION = 3
    RELATIONAL = 4

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