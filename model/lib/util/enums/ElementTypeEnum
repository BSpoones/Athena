from enum import Enum
from abc import ABC, abstractmethod
from EnumMeta import _EnumMeta


class ElementType(ABC, Enum, metaclass=_EnumMeta):
    
    @staticmethod
    def from_ordinal(ordinal: int):
        """Returns the enum member corresponding to the given ordinal."""
        members = list(ElementType)
        
        if 0 <= ordinal < len(members):
            return members[ordinal]
        raise ValueError(f"Invalid ordinal {ordinal}")
    
    @staticmethod
    def max() -> int:
        members = list(ElementType)
        if (len(members) < 1):
            return 0
        
        return list(map(members, lambda x: x.ordinal())).max()
        
    
    @staticmethod
    def min() -> int:
        members = list(ElementType)
        if (len(members) < 1):
            return 0
        
        return list(map(members, lambda x: x.ordinal())).min()
    

    def ordinal(self) -> int:
        """Returns the index (ordinal) of the enum member."""
        return list(self.__class__).index(self)
        
    @property
    @abstractmethod
    def raw_file() -> str:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def paraphrased_file() -> str:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def normalised_file() -> str:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def classified_file() -> str:
        raise NotImplementedError
    
    