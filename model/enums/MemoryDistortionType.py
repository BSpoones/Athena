from model.lib.util.enums.ElementTypeEnum import ElementType

class MemoryDistortionType(ElementType):
    FABRICATION = 1
    OVERWRITING = 2
    RETROSPECTIVE = 3
    SOCIAL = 4
    TEMPORAL = 5

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