import pytest

from reprise.api import app
from reprise.db import Base, database_context, engine


@pytest.fixture(scope="function", autouse=True)
def session():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with database_context() as session:
        yield session
        session.rollback()
        session.close()


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()
