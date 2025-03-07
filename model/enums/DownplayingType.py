from model.lib.util.enums.ElementTypeEnum import ElementType

class DownplayingType(ElementType):
    COMPARATIVE = 1
    DELAYED = 2
    EXAGGERATION = 3
    MOCKING = 4
    TRIVIALISATION = 5

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