from model.lib.util.enums.ElementTypeEnum import ElementType

class BlameType(ElementType):
    PERSONAL = 1
    CIRCUMSTANCE = 2
    REACTIVE = 3
    COMPARATIVE = 4

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