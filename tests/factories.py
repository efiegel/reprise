import factory
from factory.alchemy import SQLAlchemyModelFactory

from reprise.db import Citation, ClozeDeletion, Motif


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


def cloze_deletion_factory(session):
    class _ClozeDeletionFactory(SQLAlchemyModelFactory):
        class Meta:
            model = ClozeDeletion
            sqlalchemy_session = session
            sqlalchemy_session_persistence = "commit"

        uuid = factory.Faker("uuid4")
        created_at = factory.Faker("date_time")
        mask_tuples = [(0, 1)]  # not a sensible mask, just a populated one

        motif = factory.SubFactory(motif_factory(session))

    return _ClozeDeletionFactory
