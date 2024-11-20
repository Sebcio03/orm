import atexit
import sqlite3
from typing import Self


class Connection:
    connection: sqlite3.Connection | None = None
    cursor: sqlite3.Cursor | None = None

    def __new__(cls, database_uri: str | None = None, *args, **kwargs):
        if not cls.connection and not cls.cursor:
            if database_uri is None:
                raise Exception(
                    "Database URI is required while first time invoking connection"
                )
            cls.connection = sqlite3.connect(database_uri)
            cls.cursor = cls.connection.cursor()
            atexit.register(lambda: cls.close_db_connection)
            return super(Connection, cls).__new__(cls, *args, **kwargs)
        return super(Connection, cls).__new__(cls, *args, **kwargs)

    @classmethod
    def close_db_connection(cls) -> None:
        cls.connection.close()

    @classmethod
    def execute(cls: Self, stmt: str) -> any:
        response = cls.cursor.execute(stmt)
        cls.connection.commit()
        return response
