from model.lib.util.enums.ElementTypeEnum import ElementType

class EmotionalLeverageType(ElementType):
    ABANDONMENT = 1
    AFFECTION = 2
    GUILT = 3
    SOCIAL = 4

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