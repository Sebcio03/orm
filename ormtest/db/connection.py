import sqlite3
from typing import Self


class Connection:
    def __init__(self: Self, database_uri: str) -> None:
        self.conn = sqlite3.connect(database_uri)
        self.c = self.conn.cursor()

    def __del__(self: Self) -> None:
        self.conn.close()

    def execute(self: Self, stmt: str) -> any:
        return self.c.execute(stmt)