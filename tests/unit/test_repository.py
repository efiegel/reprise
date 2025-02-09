from reprise.repository import MotifRepository


class TestRepository:
    def test_add_motif(self, session):
        repository = MotifRepository(session)
        content, citation = "Hello, World!", "my-citation"
        motif = repository.add_motif("Hello, World!", "my-citation")
        assert motif.uuid is not None
        assert motif.created_at is not None
        assert motif.content == content
        assert motif.citation == citation

    def test_get_motif(self, session):
        repository = MotifRepository(session)
        motif = repository.add_motif("Hello, World!", "my-citation")
        assert repository.get_motif(motif.uuid) == motif

    def test_get_motifs(self, session):
        repository = MotifRepository(session)
        repository.add_motif("Hello, World!", "my-citation")
        repository.add_motif("Hello again, World!", "my-citation")
        assert len(repository.get_motifs()) == 2

    def test_update_motif_content(self, session):
        repository = MotifRepository(session)
        motif = repository.add_motif("Hello, World!", "my-citation")

        new_content = "Hello, Universe!"
        updated_motif = repository.update_motif_content(motif.uuid, new_content)
        assert updated_motif.content == new_content

    def test_delete_motif(self, session):
        repository = MotifRepository(session)
        motif = repository.add_motif("Hello, World!", "my-citation")

        repository.delete_motif(motif.uuid)
        assert repository.get_motif(motif.uuid) is None
