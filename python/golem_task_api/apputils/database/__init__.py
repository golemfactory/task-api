from pathlib import Path

import peewee
from typing import List, Type


database = peewee.DatabaseProxy()


def initialize_database(
    db: peewee.Database,
    db_path: Path,
    models: List[Type[peewee.Model]],
) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db.init(str(db_path))

    database.initialize(db)
    database.create_tables(models, safe=True)


def create_sqlite_database() -> peewee.Database:
    return peewee.SqliteDatabase(
        database=None,
        thread_safe=True,
        pragmas=(
            ('foreign_keys', True),
            ('busy_timeout', 1000),
            ('journal_mode', 'WAL'),
        ),
    )
