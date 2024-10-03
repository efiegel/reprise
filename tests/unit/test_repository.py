from reprise.repository import add_motif


class TestRepository:
    def test_add_motif(self):
        content, citation = "Hello, World!", "my-citation"
        motif = add_motif("Hello, World!", "my-citation")
        assert motif.uuid is not None
        assert motif.created_at is not None
        assert motif.content == content
        assert motif.citation == citation
