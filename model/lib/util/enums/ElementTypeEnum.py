from enum import IntEnum
from abc import ABC
from .EnumMeta import MyEnumMeta
from data import RAW_FILES


class ElementType(ABC, IntEnum, metaclass=MyEnumMeta):
    """
    DOCSTRING GO HERE

    """

    # TODO -> Add explanation
    NONE = 0

    @staticmethod
    def from_ordinal(ordinal: int):
        """Returns the enum member corresponding to the given ordinal."""

        if ordinal == 0:
            return None

        members = list(ElementType)
        
        if 1 <= ordinal < len(members):
            return members[ordinal]
        raise ValueError(f"Invalid ordinal {ordinal}")
    
    @staticmethod
    def max() -> int:
        members: list[ElementType] = list(ElementType)
        if not members:
            return 0
        
        return max(map(lambda x: x.ordinal(), members))
        
    
    @staticmethod
    def min() -> int:
        members = list(ElementType)
        if not members:
            return 0
        
        return min(map(lambda x: x.ordinal(), members))

    @classmethod
    def raw_file(cls) -> str:
        return RAW_FILES[cls.__name__]

    @classmethod
    def paraphrased_file(cls) -> str:
        raise NotImplementedError
    @classmethod
    def normalised_file(cls) -> str:
        raise NotImplementedError

    @classmethod
    def classified_file(cls) -> str:
        raise NotImplementedError


    def ordinal(self) -> int:
        """Returns the index (ordinal) of the enum member."""
        return list(self.__class__).index(self)
