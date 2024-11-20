import decimal
import logging
from typing import TypeVar, get_args

PK = TypeVar("PK")

type2sql = {
    str: "TEXT",
    bool: "INTEGER",
    int: "INTEGER",
    float: "REAL",
    decimal.Decimal: "REAL",
    bytes: "BLOB",
}


def python_type2sql(type: any) -> tuple[str, str]:
    sql_type = type2sql.get(type)
    constraints = "NOT NULL"  # Allow None if specified in type

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
            raise Exception(f"INTEGER PRIMARY KEY CANNOT BE NULL")
        logging.warning("INTEGER PRIMARY KEY CANNOT BE NULL, NOT NULL can be omitted")

    if allow_null:
        constraints = ""
    if is_pk:
        constraints = "PRIMARY KEY " + constraints

    if sql_type is None:
        raise Exception(f"Type unknown or not supported: {type}")
    return sql_type, constraints
