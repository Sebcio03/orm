from dataclasses import dataclass
from abc import ABCMeta
from typing import TypeVar

_T = TypeVar("_T")

@dataclass
class Table(ABCMeta):
    ...


    @classmethod
    def select(cls: _T, stmt: str) -> list[_T]:
        return []