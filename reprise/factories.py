import factory
from factory.alchemy import SQLAlchemyModelFactory

from reprise.db import Motif


def motif_factory(session):
    class _MotifFactory(SQLAlchemyModelFactory):
        class Meta:
            model = Motif
            sqlalchemy_session = session
            sqlalchemy_session_persistence = "commit"

        uuid = factory.Faker("uuid4")
        content = factory.Faker("text")
        citation = factory.Faker("text")
        created_at = factory.Faker("date_time")

    return _MotifFactory
