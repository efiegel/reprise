from contextlib import contextmanager
from datetime import datetime
from uuid import uuid4

from peewee import (
    CharField,
    DateTimeField,
    Model,
    SqliteDatabase,
    TextField,
)

db = SqliteDatabase("reprise.db")


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
    uuid = CharField(primary_key=True, max_length=36, default=uuid4)
    content = TextField(null=False)
    citation = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)


all_models = [Motif]
