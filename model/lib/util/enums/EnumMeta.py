from abc import ABCMeta
from enum import EnumMeta

class _EnumMeta(ABCMeta, EnumMeta):
    pass