from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from peewee import (
    AutoField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    Model,
    SqliteDatabase,
    TextField,
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


class Motif(BaseModel):
    uuid = CharField(primary_key=True, max_length=36, default=uuid4())
    content = TextField(null=False)
    citation = TextField()
    created_at = DateTimeField(default=datetime.now)


class Reprisal(BaseModel):
    id = AutoField(primary_key=True)
    motif = ForeignKeyField(Motif, backref="motif")
    created_at = DateTimeField(default=datetime.now)


all_models = [Motif, Reprisal]
