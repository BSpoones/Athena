from lib.util.enums.ElementTypeEnum import ElementType

class BlameType(ElementType):
    DIRECT = 1,
    JUSTIFIED = 2,
    REVERSE = 3
    
    @property
    def raw_rile() -> str:
        return ""
    
    @property
    def paraphrased_file() -> str:
        return ""
    
    @property
    def normalised_file() -> str:
        return ""
    
    @property
    def classified_file() -> str:
        return ""