import factory
from factory.alchemy import SQLAlchemyModelFactory

from reprise.db import Citation, Motif


def motif_factory(session):
    class _MotifFactory(SQLAlchemyModelFactory):
        class Meta:
            model = Motif
            sqlalchemy_session = session
            sqlalchemy_session_persistence = "commit"

        uuid = factory.Faker("uuid4")
        content = factory.Faker("text")
        created_at = factory.Faker("date_time")

        citation = factory.SubFactory(citation_factory(session))

    return _MotifFactory


def citation_factory(session):
    class _CitationFactory(SQLAlchemyModelFactory):
        class Meta:
            model = Citation
            sqlalchemy_session = session
            sqlalchemy_session_persistence = "commit"

        uuid = factory.Faker("uuid4")
        title = factory.Faker("text")
        created_at = factory.Faker("date_time")

    return _CitationFactory
