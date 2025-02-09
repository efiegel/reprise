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
