import pytest

from reprise.factories import motif_factory
from reprise.repository import MotifRepository


class TestRepository:
    @pytest.fixture
    def repository(self, session):
        return MotifRepository(session)

    @pytest.fixture
    def motif(self, session):
        return motif_factory(session=session).create()

    def test_add_motif(self, repository):
        content, citation = "Hello, World!", "my-citation"
        motif = repository.add_motif("Hello, World!", "my-citation")
        assert motif.uuid is not None
        assert motif.created_at is not None
        assert motif.content == content
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
