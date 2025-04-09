import factory
from factory.alchemy import SQLAlchemyModelFactory

from reprise.db import Citation, ClozeDeletion, Motif, Reprisal, ReprisalSchedule


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


def reprisal_factory(session):
    class _ReprisalFactory(SQLAlchemyModelFactory):
        class Meta:
            model = Reprisal
            sqlalchemy_session = session
            sqlalchemy_session_persistence = "commit"

        uuid = factory.Faker("uuid4")
        created_at = factory.Faker("date_time")
        set_uuid = factory.Faker("uuid4")

        motif = factory.SubFactory(motif_factory(session))
        cloze_deletion = factory.SubFactory(cloze_deletion_factory(session))

    return _ReprisalFactory


def reprisal_schedule_factory(session):
    class _ReprisalScheduleFactory(SQLAlchemyModelFactory):
        class Meta:
            model = ReprisalSchedule
            sqlalchemy_session = session
            sqlalchemy_session_persistence = "commit"

        uuid = factory.Faker("uuid4")
        reprisal_set_uuid = factory.Faker("uuid4")
        scheduled_for = factory.Faker("date_time")
        created_at = factory.Faker("date_time")

    return _ReprisalScheduleFactory
