from dataclasses import dataclass
from abc import ABCMeta
from typing import TypeVar

from ormtest.db import Connection

_T = TypeVar("_T")

class Column:
    where: str | None = None

    def __init__(self, name: str):
        self.name = name

    def eq(self, other):
        self.where = f'{self.name} = {other}'
        return self

    def __str__(self):
        return self.name


class TableMeta(type):
    def __getattr__(cls, name):
        if cls.__annotations__.get(name):
           return Column(name)
        return super(type).__getattribute__(name)

    def __iter__(self):
        from ormtest.query.builder import generate_select_stmt

        stmt = generate_select_stmt(self)
        cursor = Connection().execute(stmt)
        self.__results = cursor.fetchall()
        self.i = len(self.__results)
        return self

    def from_row(cls, values):
        for column, value in zip(cls.__annotations__.keys(), values):
            setattr(cls, column, value)
        return cls

    def __next__(self):
        if self.i > 0:
            r = self.__results[self.i - 1]
            self.i -= 1
            return self.from_row(r)
        raise StopIteration

    def __str__(self):
        columns = ''
        for column in self.__annotations__.keys():
            columns = columns + f'{column}={getattr(self, column)},'
        return f'{self.__name__}({columns[:-1]})'

@dataclass
class Table(metaclass=TableMeta):
    _select: list[Column] | None = None
    _limit: int | None = None
    _where: list[Column] | None = None

    @classmethod
    def select(cls: _T, *args) -> _T:
        cls._select = []
        for column in args:
            if column.name not in cls.__annotations__.keys():
                raise TypeError(f"{column} doesn't exist on {cls.__name__}")
            cls._select.append(column)

        return cls

    @classmethod
    def where(cls: _T, *filters: tuple[Column]) -> _T:
        cls._where = []
        for column in filters:
            if column.name not in cls.__annotations__.keys():
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
            if column.name not in cls.__annotations__.keys():
                raise TypeError(f"{column} doesn't exist on {cls.__name__}")
            setattr(cls, column, value)

        stmt = generate_insert_row_stmt(cls)
        Connection.execute(stmt)

        return cls