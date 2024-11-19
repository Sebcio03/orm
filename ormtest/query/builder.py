from typing import Type
from ormtest.schema import Table



def generate_insert_row_stmt(cls: Type[Table]) -> str:
    cls_attribiutes = vars(cls)
    columns = values = ''
    for column, datatype in cls.__annotations__.items():
        columns = columns + column + ','
        value = cls_attribiutes[column]
        if datatype is str:
             value = f"'{value}'"
        values = f'{values}{value},'

    return f"INSERT INTO {cls.__name__.lower()} ({columns[:-1]}) VALUES ({values[:-1]});"

def generate_select_stmt(cls: Type[Table]) -> str:
    select = '*'
    if cls._select is not None:
        select = ''
        for column in cls._select:
            select += f'{column.name},'
        select = select[:-1]

    if cls._where is not None:
        where = 'WHERE '
        for _filter in cls._where:
            where += f'{_filter} AND '
        where = where[:-5]

    return f'SELECT {select} FROM {cls.__name__.lower()} {where} LIMIT {cls._limit};'