import logging
from typing import Type

from ormtest.db import Connection
from ormtest.query import generate_create_table_stmt
from ormtest.schema import Table

logger = logging.getLogger(__name__)


def create_tables(connection: Connection, tables: list[Type[Table]]):
    for table in tables:
        stmt = generate_create_table_stmt(table)
        connection.execute(stmt)
        logger.info(f"CREATED {table}")