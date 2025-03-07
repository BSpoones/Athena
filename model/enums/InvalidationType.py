from model.lib.util.enums.ElementTypeEnum import ElementType

class InvalidationType(ElementType):
    DICTATORIAL = 1
    PERSPECTIVE = 2
    REALITY = 3
    WEAKNESS = 4

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