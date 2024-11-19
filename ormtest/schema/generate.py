import decimal
import logging
from typing import Type, get_args, get_origin, get_type_hints
from ormtest.schema import Table, PK

type2sql = {
    str: 'TEXT',
    bool: 'INTEGER',
    int: 'INTEGER',
    float: 'REAL',
    decimal.Decimal: 'REAL',
    bytes: 'BLOB',
}

def python_type2sql(type: any) -> tuple[str, str]:
    sql_type = type2sql.get(type)
    constraints = 'NOT NULL' # Allow None if specified in type

    is_pk = False
    allow_null = False
    for t in get_args(type):
        if t is None:
            allow_null = True
        elif t is PK:
            is_pk = True
        else:
            sql_type = type2sql.get(t)

    if sql_type is int and is_pk:
        if allow_null:
            raise Exception(f'INTEGER PRIMARY KEY CANNOT BE NULL')
        logging.warning('INTEGER PRIMARY KEY CANNOT BE NULL, NOT NULL can be omitted')

    if allow_null:
        constraints = ''
    if is_pk:
        constraints = 'PRIMARY KEY ' + constraints

    if sql_type is None:
        raise Exception(f'Type unknown or not supported: {type}')
    return sql_type, constraints


def generate_create_table_stmt(table: Type[Table]) -> str:
    columns = ''

    for column_name, type in get_type_hints(table).items():
        data_type, constraints = python_type2sql(type)
        columns += f'{column_name} {data_type} {constraints},'

    columns = columns[:-1] # Remove last ',' since it will raise exception in SQL :P
    return f'CREATE TABLE IF NOT EXISTS {table.__name__} ({columns});'