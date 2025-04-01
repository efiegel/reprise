from unittest.mock import patch

import pytest

from reprise.api import app
from reprise.db import Base, database_session, engine


@pytest.fixture(scope="function", autouse=True)
def session():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with database_session() as session:
        yield session
        session.rollback()
        session.close()


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


@pytest.fixture
def mock_openai_client():
    with patch("reprise.openai_client.get_client") as mock_get_client:
        yield mock_get_client
