import logging
import sys
from importlib import import_module
from inspect import isclass
from pathlib import Path
from typing import Type

from ormtest.cli.create_tables import create_tables
from ormtest.db import Connection
from ormtest.schema import Table

logger = logging.getLogger("CMD")
logging.basicConfig(
    format="%(asctime)s %(levelname)s\t%(message)s", level=logging.DEBUG
)

help = """
Commands to run are: 
- create_tables <path_to_project>
"""

commands = {
    "create_tables": create_tables,
}


def discover_project(path_to_project: Path) -> tuple[Connection, list[Type[Table]]]:
    connection = None
    tables = []

    for file in path_to_project.glob("**/*.py"):
        module_path = str(file).removesuffix(".py").replace("/", ".")
        module_variables = import_module(module_path).__dict__
        for key, value in module_variables.items():
            if isinstance(value, Connection):
                connection = value
            elif isclass(value) and issubclass(value, Table) and value is not Table:
                tables.append(value)

    return connection, tables


def main(cmd: str, path_to_project: str) -> None:
    command_function = commands.get(cmd)
    if not command_function:
        raise Exception(help)

    path_to_project = Path(path_to_project)
    connection, tables = discover_project(path_to_project)
    command_function(connection, tables)


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        raise Exception(help)
    main(sys.argv[1], sys.argv[2])
