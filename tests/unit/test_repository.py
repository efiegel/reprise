import pytest

from reprise.repository import CitationRepository, MotifRepository
from tests.factories import citation_factory, motif_factory


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
