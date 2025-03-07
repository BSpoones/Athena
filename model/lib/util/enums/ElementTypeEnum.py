from enum import IntEnum
from abc import ABC, abstractmethod
from EnumMeta import _EnumMeta


class ElementType(ABC, IntEnum, metaclass=_EnumMeta):
    
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

    @property
    @abstractmethod
    def raw_file(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def paraphrased_file(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def normalised_file(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def classified_file(self) -> str:
        raise NotImplementedError


    def ordinal(self) -> int:
        """Returns the index (ordinal) of the enum member."""
        return list(self.__class__).index(self)
