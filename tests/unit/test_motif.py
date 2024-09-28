from unittest.mock import patch

from reprise.motif import Motif


class TestMotif:
    def test_create_motif(self, tmp_path):
        content = "Hello, World!"
        motif = Motif(content)
        with patch.object(motif, "PERSISTENCE_DIR", tmp_path):
            motif.save()

        with open(f"{tmp_path}/{motif.uuid}.md") as file:
            assert file.read() == content
