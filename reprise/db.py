from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from peewee import (
    AutoField,
    CharField,
    DateTimeField,
    Model,
    SqliteDatabase,
)

from settings import VAULT_DIRECTORY

db = SqliteDatabase(Path(VAULT_DIRECTORY) / ".reprise" / "reprise.db")


@contextmanager
def database_context(database: SqliteDatabase = db):
    try:
        database.connect()
        database.bind(all_models, bind_refs=False, bind_backrefs=False)
        database.create_tables(all_models)
        yield database
    finally:
        if not database.is_closed():
            database.close()


class BaseModel(Model):
    class Meta:
        database = None


class Reprisal(BaseModel):
    id = AutoField(primary_key=True)
    motif_uuid = CharField(max_length=36)
    datetime = DateTimeField(default=datetime.now)


all_models = [Reprisal]
