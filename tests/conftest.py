import pytest
from peewee import SqliteDatabase

from reprise.db import all_models, database_context

test_db = SqliteDatabase(":memory:")


@pytest.fixture(scope="function", autouse=True)
def db():
    with database_context(test_db):
        yield test_db

    test_db.connect()
    test_db.drop_tables(all_models)
    test_db.close()
