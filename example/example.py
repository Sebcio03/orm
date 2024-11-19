from ormtest.db import Connection

connection_uri = 'example.db'
connection = Connection(connection_uri)

from ormtest.schema import Table, PK

class User(Table):
    id: int | PK
    name: str
    password: str

# python ormtest/cmd.py create_tables
# python ormtest/cmd.py drop_db