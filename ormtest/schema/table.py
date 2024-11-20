import logging
from abc import ABCMeta
from dataclasses import dataclass
from typing import TypeVar, Union

from ormtest.db import Connection

logger = logging.getLogger(__name__)
_T = TypeVar("_T")

class OR(list):
    def __str__(self):
        left, right = self[0], self[1]
        if left is OR:
            left = str(left)
        elif isinstance(left, Column):
            left = left.where

        if right is OR:
            right = str(right)
        elif isinstance(right, tuple):
            right = f"({right[0].where} AND {right[1].where})"
        elif isinstance(right, Column):
            right = right.where

        return f"{left} OR {right}"

    def __or__(self, other):
        return OR([self, other])

class Column:
    where: str | None = None

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return self.name

    def __or__(self, other):
        return OR([self, other])

    def eq(self, other):
        if isinstance(other, str):
            other = f"'{other}'"
        self.where = f"{self.name} = {other}"
        return self

    def gt(self, other):
        if isinstance(other, str):
            other = f"'{other}'"
        self.where = f"{self.name} > {other}"
        return self

    def gte(self, other):
        if isinstance(other, str):
            other = f"'{other}'"
        self.where = f"{self.name} >= {other}"
        return self

    def lt(self, other):
        if isinstance(other, str):
            other = f"'{other}'"
        self.where = f"{self.name} < {other}"
        return self

    def lte(self, other):
        if isinstance(other, str):
            other = f"'{other}'"
        self.where = f"{self.name} <= {other}"
        return self



class TableMeta(ABCMeta):
    def __getattr__(self, name):
        if self.__annotations__.get(name):
            return Column(name)
        return super(type).__getattribute__(name)

    def __iter__(self):
        from ormtest.query.builder import generate_select_stmt

        stmt = generate_select_stmt(self)
        Connection.execute(stmt)
        self.__results = Connection.cursor.fetchall()
        self.i = len(self.__results)
        return self

    def from_row(cls, values):
        for column, value in zip(cls.__annotations__.keys(), values):
            setattr(cls, column, value)
        return cls

    def __next__(self):
        if self.i > 0:
            self.i -= 1
            r = self.__results[self.i]
            return self.from_row(r)
        raise StopIteration

    def __str__(self):
        columns = ""
        for column in self.__annotations__.keys():
            columns = columns + f"{column}={getattr(self, column)},"
        return f"{self.__name__}({columns[:-1]})"


@dataclass
class Table(metaclass=TableMeta):
    _select: list[Column] | None = None
    _limit: int | None = None
    _where: list[Column] | None = None

    @classmethod
    def select(cls: _T, *args) -> _T:
        cls._select = []
        for column in args:
            if str(column) not in cls.__annotations__.keys():
                raise TypeError(f"{column} doesn't exist on {cls.__name__}")
            cls._select.append(column)

        return cls

    @classmethod
    def where(cls: _T, *filters: tuple[Column]) -> _T:
        cls._where = []
        for column in filters:
            if isinstance(
                column, OR
            ):
                cls._where.append(str(column))
            else:
                if str(column) not in cls.__annotations__.keys():
                    raise TypeError(f"{column} doesn't exist on {cls.__name__}")
                cls._where.append(column.where)

        return cls

    @classmethod
    def limit(cls: _T, limit: int) -> _T:
        cls._limit = limit
        return cls

    @classmethod
    def create(cls: _T, **kwargs) -> _T:
        from ormtest.query.builder import generate_insert_row_stmt

        for column, value in kwargs.items():
            if str(column) not in cls.__annotations__.keys():
                raise TypeError(f"{column} doesn't exist on {cls.__name__}")
            setattr(cls, column, value)

        stmt = generate_insert_row_stmt(cls)
        Connection.execute(stmt)

        return cls
