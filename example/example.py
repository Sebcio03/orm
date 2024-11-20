from ormtest.db import Connection

connection_uri = "example.db"
connection = Connection(connection_uri)

from ormtest.schema import PK, Table


class User(Table):
    id: int | PK
    name: str
    password: str


# python ormtest/cmd.py create_tables

for i in range(10):
    User.create(
        id=i,
        name=f"<NAME{i}>",
        password=f"<PASSWORD{i}>",
    )


for i in User.select(User.id, User.name).where(User.id.eq(1)).limit(5):
    print(i)
