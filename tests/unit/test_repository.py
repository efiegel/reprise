from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from reprise.repository import (
    CitationRepository,
    ClozeDeletionRepository,
    MotifRepository,
    ReprisalRepository,
    ReprisalScheduleRepository,
)
from tests.factories import (
    citation_factory,
    cloze_deletion_factory,
    motif_factory,
    reprisal_factory,
    reprisal_schedule_factory,
)


class TestMotifRepository:
    @pytest.fixture
    def repository(self, session):
        return MotifRepository(session)

    @pytest.fixture
    def motif(self, session):
        return motif_factory(session=session).create()

    def test_add_motif(self, repository):
        content = "Hello, World!"
        motif = repository.add_motif("Hello, World!")
        assert motif.uuid is not None
        assert motif.created_at is not None
        assert motif.content == content

    def test_add_motif_with_citation(self, repository, session):
        citation = citation_factory(session=session).create()
        motif = repository.add_motif("Hello, World!", citation)
        assert motif.citation == citation

    def test_get_motif(self, repository, motif):
        assert repository.get_motif(motif.uuid) == motif

    def test_get_motifs(self, session, repository):
        motif_factory(session=session).create_batch(2)
        assert len(repository.get_motifs()) == 2

    def test_update_motif_content(self, repository, motif):
        new_content = "Hello, Universe!"
        updated_motif = repository.update_motif_content(motif.uuid, new_content)
        assert updated_motif.content == new_content

    def test_delete_motif(self, repository, motif):
        repository.delete_motif(motif.uuid)
        assert repository.get_motif(motif.uuid) is None

    def test_add_citation(self, repository, motif, session):
        citation = citation_factory(session=session).create()
        motif = repository.add_citation(motif.uuid, citation)
        assert motif.citation == citation

    def test_get_motifs_paginated(self, session, repository):
        motif_factory(session=session).create_batch(15)
        page_size = 5

        # first page
        motifs_page_1 = repository.get_motifs_paginated(page=1, page_size=page_size)
        assert len(motifs_page_1) == page_size

        # first page
        motifs_page_2 = repository.get_motifs_paginated(page=2, page_size=page_size)
        assert len(motifs_page_2) == page_size

        # remaining motifs
        motifs_page_3 = repository.get_motifs_paginated(page=3, page_size=page_size)
        assert len(motifs_page_3) == 5

        # empty page
        motifs_page_4 = repository.get_motifs_paginated(page=4, page_size=page_size)
        assert len(motifs_page_4) == 0

    def test_get_motifs_count(self, session, repository):
        motif_factory(session=session).create_batch(10)
        assert repository.get_motifs_count() == 10

    def test_get_motifs_with_cloze_deletions(self, session, repository):
        motif_with_cd = motif_factory(session=session).create()
        cloze_deletion_factory(session=session).create(motif=motif_with_cd)

        motif_factory(session=session).create()  # motif without cloze deletion
        assert len(repository.get_motifs_with_cloze_deletions()) == 1


class TestCitationRepository:
    @pytest.fixture
    def repository(self, session):
        return CitationRepository(session)

    @pytest.fixture
    def citation(self, session):
        return citation_factory(session=session).create()

    def test_get_citation(self, repository, citation):
        assert repository.get_citation(citation.uuid) == citation

    def test_get_citations(self, session, repository):
        citation_factory(session=session).create_batch(2)
        assert len(repository.get_citations()) == 2

    def test_add_citation(self, repository):
        title = "Hello, World!"
        citation = repository.add_citation(title)
        assert citation.uuid is not None
        assert citation.created_at is not None
        assert citation.title == title

    def test_get_citation_by_title(self, repository, citation):
        assert repository.get_citation_by_title(citation.title) == citation


class TestReprisalRepository:
    @pytest.fixture
    def repository(self, session):
        return ReprisalRepository(session)

    def test_add_reprisal(self, repository, session):
        motif = motif_factory(session=session).create()
        set_uuid = str(uuid4())

        reprisal = repository.add_reprisal(motif.uuid, set_uuid)
        assert reprisal.uuid is not None
        assert reprisal.created_at is not None
        assert reprisal.set_uuid == set_uuid
        assert reprisal.motif == motif

    def test_reprise_with_cloze_deletion(self, repository, session):
        motif = motif_factory(session=session).create(content="the sky is blue")
        cloze_deletion = cloze_deletion_factory(session=session).create(
            motif=motif, mask_tuples=[(11, 14)]
        )

        set_uuid = str(uuid4())
        reprisal = repository.add_reprisal(motif.uuid, set_uuid, cloze_deletion.uuid)
        assert reprisal.cloze_deletion == cloze_deletion
        assert reprisal.motif == motif


class TestClozeDeletionRepository:
    @pytest.fixture
    def repository(self, session):
        return ClozeDeletionRepository(session)

    def test_add_cloze_deletion(self, repository, session):
        motif_content = "the sky is blue"
        motif = motif_factory(session=session).create(content=motif_content)

        cloze_deletion = repository.add_cloze_deletion(motif.uuid, [(11, 14)])
        assert cloze_deletion.uuid is not None
        assert cloze_deletion.created_at is not None
        assert cloze_deletion.mask_tuples == [(11, 14)]
        assert cloze_deletion.motif == motif
        assert motif.cloze_deletions == [cloze_deletion]

    def test_get_cloze_deletion(self, repository, session):
        motif = motif_factory(session=session).create(content="the sky is blue")
        cloze_deletion = repository.add_cloze_deletion(motif.uuid, [(11, 14)])

        fetched_cloze_deletion = repository.get_cloze_deletion(cloze_deletion.uuid)
        assert fetched_cloze_deletion == cloze_deletion
        assert fetched_cloze_deletion.mask_tuples == [(11, 14)]
        assert fetched_cloze_deletion.motif == motif

    def test_update_cloze_deletion(self, repository, session):
        motif = motif_factory(session=session).create(content="the sky is blue")
        cloze_deletion = repository.add_cloze_deletion(motif.uuid, [(11, 14)])

        updated_cloze_deletion = repository.update_cloze_deletion(
            cloze_deletion.uuid, [(4, 6), (11, 14)]
        )
        assert updated_cloze_deletion.mask_tuples == [(4, 6), (11, 14)]
        assert updated_cloze_deletion.motif == motif

    def test_delete_cloze_deletion(self, repository, session):
        motif = motif_factory(session=session).create(content="the sky is blue")
        cloze_deletion = repository.add_cloze_deletion(motif.uuid, [(11, 14)])

        repository.delete_cloze_deletion(cloze_deletion.uuid)
        assert repository.get_cloze_deletion(cloze_deletion.uuid) is None

    def test_mask(self, repository, session):
        motif_content = "the sky is blue"
        motif = motif_factory(session=session).create(content=motif_content)

        cd1 = repository.add_cloze_deletion(motif.uuid, [(11, 14)])
        cd2 = repository.add_cloze_deletion(motif.uuid, [(4, 6), (11, 14)])
        assert cd1.masked_motif() == "the sky is *"
        assert cd2.masked_motif("___") == "the ___ is ___"

    def test_masked_words(self, repository, session):
        motif_content = "the sky is blue"
        motif = motif_factory(session=session).create(content=motif_content)

        cd1 = repository.add_cloze_deletion(motif.uuid, [(11, 14)])
        cd2 = repository.add_cloze_deletion(motif.uuid, [(4, 6), (11, 14)])
        assert cd1.masked_words() == ["blue"]
        assert cd2.masked_words() == ["sky", "blue"]


class TestReprisalScheduleRepository:
    @pytest.fixture
    def repository(self, session):
        return ReprisalScheduleRepository(session)

    def test_get_reprisal_schedules(self, repository, session):
        # Create multiple schedules with different scheduled_for dates
        schedules = []
        for i in range(3):
            schedule = reprisal_schedule_factory(session).create(
                scheduled_for=datetime.now() + timedelta(days=i)
            )
            schedules.append(schedule)

        # Get all schedules and verify they are ordered by scheduled_for in descending order
        fetched_schedules = repository.get_reprisal_schedules()
        assert len(fetched_schedules) == 3
        assert fetched_schedules[0].scheduled_for > fetched_schedules[1].scheduled_for
        assert fetched_schedules[1].scheduled_for > fetched_schedules[2].scheduled_for

    def test_add_reprisal_schedule(self, repository, session):
        reprisal = reprisal_factory(session=session).create()
        reprisal_set_uuid = reprisal.set_uuid
        scheduled_for = datetime.now() + timedelta(days=1)

        schedule = repository.add_reprisal_schedule(reprisal_set_uuid, scheduled_for)
        assert schedule.uuid is not None
        assert schedule.created_at is not None
        assert schedule.reprisal_set_uuid == reprisal_set_uuid
        assert schedule.scheduled_for == scheduled_for

    def test_add_reprisal_schedule_nonexistent_set(self, repository):
        nonexistent_set_uuid = str(uuid4())
        scheduled_for = datetime.now() + timedelta(days=1)

        with pytest.raises(ValueError) as exc_info:
            repository.add_reprisal_schedule(nonexistent_set_uuid, scheduled_for)
        assert str(exc_info.value) == f"Reprisal set {nonexistent_set_uuid} not found"
