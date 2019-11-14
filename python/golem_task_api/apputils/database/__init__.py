from pathlib import Path

import peewee
from typing import Iterable, Type


database = peewee.DatabaseProxy()


def initialize_database(
    db: peewee.Database,
    db_path: Path,
    models: Iterable[Type[peewee.Model]],
) -> None:
    """ Initialize and bind the corresponding database instance
        to the database proxy. Create tables for the given models """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db.init(str(db_path))

    database.initialize(db)
    database.create_tables(models, safe=True)
