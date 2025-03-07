from model.lib.util.enums.ElementTypeEnum import ElementType

class ComparativeJustificationType(ElementType):
    EXTERNAL = 1
    POST_HARDSHIP = 2
    SOCIAL = 3
    WORST_CASE = 4

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